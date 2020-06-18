# Kostal Modbus interface for realtime solar data
from pyModbusTCP import utils
from pyModbusTCP.client import ModbusClient
from termcolor import colored
from ww import f
from datetime import datetime


class Kostal:
    import time

    cacheTime = 10
    config = None
    configConfig = None
    configKostal = None
    debugLevel = 0
    fetchFailed = False
    lastFetch = 0
    master = None
    serverIP = None
    serverPort = 80
    status = False
    timeout = 10
    voltage = 0
    totalDCPower = 0
    home_fromGrid = 0
    home_fromSolar = 0
    client = None

    def __init__(self, master):
        self.master = master
        self.config = master.config
        try:
            self.configConfig = master.config["config"]
        except KeyError:
            self.configConfig = {}
        try:
            self.configKostal = master.config["sources"]["Kostal"]
        except KeyError:
            self.configKostal = {}
        self.debugLevel = self.configConfig.get("debugLevel", 0)
        self.status = self.configKostal.get("enabled", False)
        self.serverIP = self.configKostal.get("serverIP", None)
        self.modbusPort = self.configKostal.get("modbusPort", 1502)
        self.unitID = self.configKostal.get("unitID", 71)

        # Unload if this module is disabled or not properly configured
        if ((not self.status) or (not self.serverIP)
                or (int(self.serverPort) < 1)):
            self.master.releaseModule("lib.TWCManager.EMS", "Kostal")

    def time_now(self):
        return datetime.now().strftime(
            "%H:%M:%S" + (".%f" if self.config["config"]["displayMilliseconds"] else "")
        )

    def debugLog(self, min_level, message):
        if self.debugLevel >= min_level:
            print(
                colored(self.time_now() + " ", "yellow")
                + colored(f("Kostal    "), "green")
                + colored(f(" {min_level} "), "cyan")
                + f("{message}")
            )

    def readModbus(self, register):
        # read the given modbus register as float, big endian coded, 2 bytes
        value_raw = self.client.read_holding_registers(register, 2)

        if value_raw:
            value = utils.decode_ieee((value_raw[1] << 16) + value_raw[0])
        else:
            value = None

        return value

    def updateTotalDCPower(self):
        self.totalDCPower = self.readModbus(100)
        self.debugLog(10, "Total DC power available: " + f'{self.totalDCPower:5.2f}' + " W")

    def updateHomeFromGrid(self):
        self.home_fromGrid = self.readModbus(108)
        self.debugLog(10, "Home consumption from Grid: " + f'{self.home_fromGrid:5.2f}' + " W")

    def updateHomeFromSolar(self):
        self.home_fromSolar = self.readModbus(116)
        self.debugLog(10, "Home consumption from Solar: " + f'{self.home_fromSolar:5.2f}' + " W")

    def getConsumption(self):
        if not self.status:
            self.debugLog(10, "Kostal EMS Module Disabled. Skipping getConsumption")
            return 0

        # Perform updates if necessary
        self.update()

        # Return consumption value. If house is not consuming energy from the grid
        # Consumption is the difference between energy generated by the inverter and
        # energy send as a surplus to the grid

        if (self.home_fromSolar > 0.0) & (self.home_fromGrid > 0.0):
            self.debugLog(5, "Providing consumption GRID+SOLAR = " + str(self.home_fromGrid + self.home_fromSolar))
            return float(self.home_fromGrid + self.home_fromSolar)
        elif (self.home_fromSolar > 0.0) & (self.home_fromGrid <= 0.0):
            self.debugLog(5, "Providing consumption SOLAR = " + str(self.home_fromSolar))
            return float(self.home_fromSolar)
        else:
            self.debugLog(5, "Providing consumption from GRID = " + str(self.home_fromGrid))
            return float(self.home_fromGrid)

    def getGeneration(self):
        if not self.status:
            self.debugLog(10, "Kostal EMS Module Disabled. Skipping getGeneration")
            return 0

        # Perform updates if necessary
        self.update()

        # Return generation value
        return float(self.totalDCPower)

    def update(self):
        if (int(self.time.time()) - self.lastFetch) > self.cacheTime:
            # Cache has expired. Fetch values from inverter via Modbus

            self.fetchFailed = False
            try:
                # open Modbus connection for reading
                self.client = ModbusClient(self.serverIP, port=self.modbusPort, unit_id=self.unitID, auto_open=True)
            except ValueError:
                self.debugLog(0, "Error connection to Kostal Inverter via Modbus")
                self.fetchFailed = True
                return 0

            self.updateTotalDCPower()
            self.updateHomeFromGrid()
            self.updateHomeFromSolar()

            # close Modbus connection
            self.client.close()

            if self.fetchFailed is not True:
                self.lastFetch = int(self.time.time())

            # Update last fetch time if successful
            return True
        else:
            # Cache time has not elapsed since last fetch, serve from cache.
            return False
