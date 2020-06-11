# ouimeaux

Open source control for Belkin WeMo devices

* Free software: BSD license
* Documentation: http://ouimeaux.rtfd.org.

## Features

* Supports WeMo Switch, Light Switch, Insight Switch and Motion
* Command-line tool to discover and control devices in your environment
* REST API to obtain information and perform actions on devices
* Simple responsive Web app provides device control on mobile
* Python API to interact with device at a low level

## Installation

```
$ sudo pip install virtualenv
$ mkdir ouimeaux-env
$ virtualenv ouimeaux-env
$ source ouimeaux-env/bin/activate
$ cd ouimeaux-env
$ pip install git+https://github.com/iancmcc/ouimeaux.git
```

At this point you should be able to use `wemo` and `wemo server` so long as
you've activated your environment with `source ouimeaux-env/bin/activate`.

**Note:** Ensure that the `pip` and `virtualenv` command you use belongs to a
Python 2 installation. On some systems, there are multiple versions of Python
installed. See below for an example from my Fedora system.

```
$ /bin/ls -1 "$(dirname $(which python))/virtualenv"{,-2} "$(dirname $(which python))/p"{ython,ip}[23]
/usr/bin/pip2
/usr/bin/pip3
/usr/bin/python2
/usr/bin/python3
/usr/bin/virtualenv
/usr/bin/virtualenv-2

$ pip --version
pip 9.0.1 from /usr/lib/python3.5/site-packages (python 3.5)

$ pip2 --version
pip 9.0.1 from /usr/lib/python2.7/site-packages (python 2.7)
```

## HTTP client version

The `client.py` script provided by [BlackLight](https://github.com/BlackLight)
allows the user to send simple commands to a device without the cumbersome
(and [currently broken](https://github.com/iancmcc/ouimeaux/issues/193)) `Discoverer`
object.

Requirements: install requests:

```
pip install requests
```

You can run client.py in two modes:

### Scan mode

Will scan for available WeMo Switch devices on the network. Example:

```
python client.py --scan --subnet 192.168.1.0/24
```

### Action mode

Will run an action on a specified device. Example:

```
python client.py --device 192.168.1.19 --on
```

With no `--on|--off|--toggle` action specified the script will return a JSON
with the device info:

```json
{
  "device": "192.168.1.19",
  "name": "Lightbulbs",
  "state": false
}
```

Run `python client.py --help` for more info about the available options.

## Troubleshooting

#### Using a VPN 
The `wemo` command won't be able to communicate with your devices if you're connected to a VPN. It may be redirecting UDP traffic somewhere else. Disconnect from the VPN and the tool should work.

Open an issue and I'll try to help.
