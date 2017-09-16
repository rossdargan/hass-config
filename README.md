# Home Assitant Config ![Build](https://travis-ci.org/rossdargan/hass-config.svg?branch=master)

This is my config! I'm running inside docker (running on ubuntu 16). I have several other parts running on docker including my continuous integration.

My continuous integration uses this [docker image](https://hub.docker.com/r/rossdargan/travis-ci-webhook/) as a webhook from travis. This writes a file onto my docker host. Locally I have a cron'd job that detects this file and performs a git pull, followed by a docker restart to update the config in Hass.

**Software in use**
* Mosquitto docker image

**Custom Sensors**
* [Monzo sensor] (https://github.com/rossdargan/monzo-hass-sensor) *This displays the balance in one of my accounts. I get alerts when it dips below a certain level*

**Devices in use**

* Nvida Shield
* Chromecast audios throughout the house
* Google Home
* 2 * Echo dots
* Echo
* Philips TV
* Philips Hue (Gen1)
* Philips Hue Dimmer
* Philips Hue Tap
* Philips Hue Motion Sensor
* Apple phones/tablets and an Android phone.
* 7 Hue Colour bulbs
* 2 Hue White bulbs
* 2 Hue light strips
* A Hue bloom
* 4 Zwave light switches
* 2 * Next Protects
* Nest Thermostat
* Ring Door bell
* Alarm with a com port
  * Uses these docker images I manage
    * [ls30 daemon](https://hub.docker.com/r/rossdargan/ls30daemon/) Acts as a proxy to allow multiple devices to subscribe to the com port
    * [ls30 watchdog](https://hub.docker.com/r/rossdargan/ls30watchdog/) Monitors the alarm for events, and send it to the message queue
    * [ls30 mqtt](https://hub.docker.com/r/rossdargan/ls30mqtt/): Allows control of the alarm from a message queue
* "Smart" greenhouse  *This allows me to monitor water levels, temperature, light and humidity in my greenhouse*
  * Uses [this](https://github.com/rossdargan/Greenhouse) code on an arduino


... more to follow!
