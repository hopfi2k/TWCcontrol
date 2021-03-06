# Settings

The following settings (outside of the configuration file) are available via the inbuilt Web Interface:

## Stop Charging Method

This option, which defaults to using the Tesla API, allows you to specify how you would like TWCManager to stop a car from charging. The following options exist, and each has some information to help you decide on which approach to use:

   * Tesla API
      * This method will use the Tesla API to send a stop charging message to vehicles which are detected as being "at home".
      * This method is only effective for Tesla vehicles. Any non-Tesla vehicles are not visible via the Tesla API and will not be stopped, even if the available power falls below the minimum power per TWC.
      * For those vehicles, they will continue to charge, but at the minimum power per TWC rate.
   * Stop Responding to Slaves
      * This method will cause TWCManager to stop responding to Slave TWCs when the allocated amps per TWC falls below the minimum amps per TWC value. It takes approximately 30 seconds from the moment that we stop responding to slaves until they stop charging connected vehicles.
      * This has the effect, if any vehicle is connected (not just Tesla vehicles) of stopping the TWC from offering charge to a vehicle. The green light on the TWC will remain steady, whilst the red light will blink on the TWC whilst the communication ceases, and no updates will be recieved from a TWC for that period of time.
      * For non-Tesla vehicles, this has the effect of stopping them from charging. It is not known on a per-vehicle basis (until more information is submitted) what the behaviour of those vehicles are.
      * For Tesla vehicles, this method is effective up to three times during a single charging session. The vehicle will allow this until the third instance, at which point it will refuse to resume charging until it is unplugged and re-plugged.
   * Send stop command
      * For TWCs running version v4.5.3 or later, there is a stop command embedded in the Firmware. The stop command appears to take the approach of disconnecting the relay, without sending any CAN bus messages.
      * With the DIP switch in position 1 (CAN protocol enabled), this has the unfortunate outcome for Tesla vehicles of entirely stopping the vehicle from charging immediately on reciept of the message. 
      * With the DIP switch in position 2 (CAN protocol disabled), it will stop Tesla vehicles from charging, but the vehicle will eventually (after a number of interruptions) decide that the charger is broken and will refuse to start charging again.
      * [This thread](https://teslamotorsclub.com/tmc/threads/new-wall-connector-load-sharing-protocol.72830/page-24) provides the observations of those who have tested this command.
      * Whilst this option is offered primarily for the benefit of non-Tesla vehicles, it's not recommended for use with Tesla vehicles.
