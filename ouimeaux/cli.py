import os
import sys
import logging
import argparse

from .upnp import UPnPLoopbackException
from .environment import Environment
from .config import get_cache, in_home, WemoConfiguration
from .utils import matcher


NOOP = lambda *x: None


def _state(device, readable=False):
    state = device.get_state(force_update=True)
    if readable:
        return "on" if state else "off"
    else:
        return state


def scan(args, on_switch=NOOP, on_motion=NOOP):
    try:
        env = Environment(on_switch, on_motion, with_subscribers=False,
                          bind=args.bind, with_cache=args.use_cache)
        env.start()
        with get_cache() as c:
            if c.empty:
                args.use_cache = False
        if (args.use_cache is not None and not args.use_cache) or (
                    env._config.cache is not None and not env._config.cache):
            env.discover(args.timeout)
    except KeyboardInterrupt:
        sys.exit(0)
    except UPnPLoopbackException:
        print """
Loopback interface is being used! You will probably not receive any responses 
from devices.  Use ifconfig to find your IP address, then either pass the 
--bind argument or edit ~/.wemo/config.yml to specify the IP to which devices 
should call back during discovery.""".strip()
        sys.exit(1)


def switch(args):
    if args.state.lower() in ("on", "1", "true"):
        state = "on"
    elif args.state.lower() in ("off", "0", "false"):
        state = "off"
    elif args.state.lower() == "toggle":
        state = "toggle"
    elif args.state.lower() == "status":
        state = "status"
    else:
        print """No valid action specified. 
Usage: wemo switch NAME (on|off|toggle|status)"""
        sys.exit(1)

    device_name = args.device
    alias = WemoConfiguration().aliases.get(device_name)
    if alias:
        matches = lambda x:x == alias
    elif device_name:
        matches = matcher(device_name)
    else:
        matches = NOOP

    def on_switch(switch):
        if matches(switch.name):
            if state == "toggle":
                found_state = switch.get_state(force_update=True)
                switch.set_state(not found_state)
            elif state == "status":
                print _state(switch, args.human_readable)
            else:
                getattr(switch, state)()
            sys.exit(0)

    scan(args, on_switch)
    # If we got here, we didn't find anything
    print "No device found with that name."
    sys.exit(1)


def list_(args):

    def on_switch(switch):
        print "Switch:", switch.name

    def on_motion(motion):
        print "Motion:", motion.name

    scan(args, on_switch, on_motion)


def status(args):

    def on_switch(switch):
        print "Switch:", switch.name, '\t', _state(switch, args.human_readable)

    def on_motion(motion):
        print "Motion:", motion.name, '\t', _state(motion, args.human_readable)

    scan(args, on_switch, on_motion)


def clear(args):
    for fname in 'cache', 'cache.db':
        filename = in_home('.wemo', fname)
        try:
            os.remove(filename)
        except OSError:
            # File didn't exist; cache must be clear
            pass
    print "Device cache cleared."


def wemo():
    parser = argparse.ArgumentParser()

    parser.add_argument("-b", "--bind", default=None,
                        help="ip:port to which to bind the response server."
                             " Default is localhost:54321")
    parser.add_argument("-d", "--debug", action="store_true", default=False,
                        help="Enable debug logging")
    parser.add_argument("-e", "--exact-match", action="store_true", 
                        default=False,
                        help="Disable fuzzy matching for device names")
    parser.add_argument("-f", "--no-cache", dest="use_cache", default=None,
                        action="store_false",
                        help="Disable the device cache")
    parser.add_argument("-v", "--human-readable", dest="human_readable", 
                        action="store_true", default=False,
                        help="Print statuses as human-readable words")
    parser.add_argument("-t", "--timeout", type=int, default=5,
                        help="Time in seconds to allow for discovery")
    subparsers = parser.add_subparsers()

    clearparser = subparsers.add_parser("clear", 
                                        help="Clear the device cache")
    clearparser.set_defaults(func=clear)

    statusparser = subparsers.add_parser("status", 
                                         help="Print status of WeMo devices")
    statusparser.set_defaults(func=status)

    stateparser = subparsers.add_parser("switch",
                                        help="Turn a WeMo Switch on or off")
    stateparser.add_argument("device", help="Name or alias of the device")
    stateparser.add_argument("state", help="'on' or 'off")
    stateparser.set_defaults(func=switch)

    listparser = subparsers.add_parser("list",
                          help="List all devices found in the environment")
    listparser.set_defaults(func=list_)

    args = parser.parse_args()

    if getattr(args, 'debug', False):
        logging.basicConfig(level=logging.DEBUG)

    args.func(args)
