## SuperOcto v.1.0 ##
Workspace for SuperOcto by Officine Digitali Marchigiane
## Setup ##
### Requirements ###
* sudo apt-get install usbmount
### Getting and installing SuperOcto ###
```
cd ~
git clone https://github.com/mcecchi/SuperOcto.git
cp ~/SuperOcto/virtual_printer/* ~/OctoPrint/venv/lib/python2.7/site-packages/octoprint/plugins/virtual_printer
cd ~/SuperOcto/Meta-Reader/
octoprint dev plugin:install
cd ~/SuperOcto/OctoPrint-FirmwareUpdater/
octoprint dev plugin:install
cd ~/SuperOcto/RoboLCD/
octoprint dev plugin:install
```
### Settings ###
* You need to edit ~/.octoprint/config.yaml and add or modify the following section (see ~/SuperOcto/config.yaml):
```
devel:
  virtualPrinter:
    brokenM29: true
    commandBuffer: 4
    echoOnM117: true
    enabled: true
    extendedSdFileList: false
    forceChecksum: false
    hasBed: true
    includeCurrentToolInTemps: true
    includeFilenameInOpened: true
    movementSpeed:
      e: 300
      x: 6000
      y: 6000
      z: 200
    numExtruders: 1
    okAfterResend: false
    okWithLinenumber: false
    repetierStyleResends: false
    repetierStyleTargetTemperature: false
    rxBuffer: 64
    sendWait: false
    smoothieTemperatureReporting: false
    supportM112: true
    throttle: 0.01
    waitInterval: 1
plugins:
  RoboLCD:
    Model: Robo C2
    Temp_Preset:
      Robo ABS:
        Bed: 100
        Extruder1: 230
      Robo PLA:
        Bed: 60
        Extruder1: 190
printerProfiles:
  default: _default
  defaultProfile:
    axes:
      e:
        inverted: false
        speed: 300
      x:
        inverted: false
        speed: 6000
      y:
        inverted: false
        speed: 6000
      z:
        inverted: false
        speed: 200
    color: default
    extruder:
      count: 1
      nozzleDiameter: 0.4
      offsets:
      - - 0.0
        - 0.0
      sharedNozzle: false
    heatedBed: true
    id: _default
    model: Robo C2
    name: Default
    volume:
      custom_box: false
      depth: 200.0
      formFactor: rectangular
      height: 200.0
      origin: lowerleft
      width: 200.0
```

## Attributions ##
Victor E Fimbres & Matt Pedler & Peri Smith (https://github.com/victorevector/RoboLCD)

