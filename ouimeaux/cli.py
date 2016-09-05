import sys
import logging
import argparse

from .discovery import UPnPLoopbackException
from .environment import Environment
from .config import WemoConfiguration
from .utils import matcher

reqlog = logging.getLogger("requests.packages.urllib3.connectionpool")
reqlog.disabled = True

NOOP = lambda *x: None


def _state(device, readable=False):
    state = device.get_state(force_update=True)
    if readable:
        return "on" if state else "off"
    else:
        return state


def scan(args, on_switch=NOOP, on_motion=NOOP, on_bridge=NOOP, on_maker=NOOP):
    try:
        env = Environment(on_switch, on_motion, on_bridge, on_maker,
                          with_subscribers=False, bind=args.bind)
        env.start()
        env.discover(args.timeout)
    except KeyboardInterrupt:
        sys.exit(0)
    except UPnPLoopbackException:
        print("""
Loopback interface is being used! You will probably not receive any responses
from devices.  Use ifconfig to find your IP address, then either pass the
--bind argument or edit ~/.wemo/config.yml to specify the IP to which devices
should call back during discovery.""".strip())
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
        print("""No valid action specified.
Usage: wemo switch NAME (on|off|toggle|status)""")
        sys.exit(1)

    matches = make_matcher(args.device)

    def on_switch(switch):
        if matches(switch.name):
            if state == "toggle":
                found_state = switch.get_state(force_update=True)
                switch.set_state(not found_state)
            elif state == "status":
                print(_state(switch, args.human_readable))
            else:
                getattr(switch, state)()
            if args.device.lower() != 'all':
                sys.exit(0)

    scan(args, on_switch)
    # If we got here, we didn't find anything
    print("No device found with that name.")
    sys.exit(1)


def light(args):
    if args.state.lower() in ("on", "1", "true"):
        state = "on"
    elif args.state.lower() in ("off", "0", "false"):
        state = "off"
    elif args.state.lower() == "toggle":
        state = "toggle"
    elif args.state.lower() == "status":
        state = "status"
    else:
        print("""No valid action specified.
Usage: wemo light NAME (on|off|toggle|status)""")
        sys.exit(1)

    matches = make_matcher(args.name)

    def on_switch(switch):
        pass

    def on_motion(motion):
        pass

    def on_bridge(bridge):
        bridge.bridge_get_lights()
        bridge.bridge_get_groups()
        for light in bridge.Lights:
            if matches(light):
                if args.state == "toggle":
                    found_state = bridge.light_get_state(bridge.Lights[light]).get('state')
                    bridge.light_set_state(bridge.Lights[light], state=not found_state)
                elif args.state == "status":
                    print(bridge.light_get_state(bridge.Lights[light]))
                else:
                    if args.dim == None and args.state == "on":
                        dim = bridge.light_get_state(bridge.Lights[light]).get('dim')
                        state = 1
                    elif args.state == "off":
                        dim = None
                        state = 0
                    elif args.dim <= 255 and args.dim >= 0:
                        dim = args.dim
                        state = 1
                    else:
                        print("""Invalid dim specified.
Dim must be between 0 and 255""")
                        sys.exit(1)
                    bridge.light_set_state(bridge.Lights[light], state=state, dim=dim)
                if args.name != 'all':
                    sys.exit(0)
        for group in bridge.Groups:
            if matches(group):
                if args.state == "toggle":
                    found_state = bridge.group_get_state(bridge.Groups[group]).get('state')
                    bridge.group_set_state(bridge.Groups[group], state=not found_state)
                elif args.state == "status":
                    print(bridge.group_get_state(bridge.Groups[group]))
                else:
                    if args.dim == None and args.state == "on":
                        dim = bridge.group_get_state(bridge.Groups[group]).get('dim')
                        state = 1
                    elif args.state == "off":
                        dim = None
                        state = 0
                    elif args.dim <= 255 and args.dim >= 0:
                        dim = args.dim
                        state = 1
                    else:
                        print("""Invalid dim specified.
Dim must be between 0 and 255""")
                        sys.exit(1)
                    bridge.group_set_state(bridge.Groups[group], state=state, dim=dim)
                sys.exit(0)

    scan(args, on_switch, on_motion, on_bridge)
    # If we got here, we didn't find anything
    print("No device or group found with that name.")
    sys.exit(1)


def make_matcher(device_name):
    alias = WemoConfiguration().aliases.get(device_name)
    if device_name.lower() in ('all', 'any'):
        matches = lambda x: True
    elif alias:
        matches = lambda x: x == alias
    elif device_name:
        matches = matcher(device_name)
    else:
        matches = NOOP
    return matches


def maker(args):
    if args.state.lower() in ("on", "1", "true"):
        state = "on"
    elif args.state.lower() in ("off", "0", "false"):
        state = "off"
    elif args.state.lower() == "toggle":
        state = "toggle"
    elif args.state.lower() == "sensor":
        state = "sensor"
    elif args.state.lower() == "switch":
        state = "switch"
    else:
        print("""No valid action specified.
Usage: wemo maker NAME (on|off|toggle|sensor|switch)""")
        sys.exit(1)

    matches = make_matcher(args.device)

    def on_switch(maker):
        return

    def on_motion(maker):
        return

    def on_bridge(maker):
        return

    def on_maker(maker):
        if matches(maker.name):
            if state == "toggle":
                found_state = maker.get_state(force_update=True)
                maker.set_state(not found_state)
            elif state == "sensor":
                if maker.has_sensor:
                    if args.human_readable:
                        if maker.sensor_state:
                            sensorstate = 'Sensor not triggered'
                        else:
                            sensorstate = 'Sensor triggered'
                        print(sensorstate)
                    else:
                        print(maker.sensor_state)
                else:
                    print("Sensor not present")
            elif state == "switch":
                if maker.switch_mode:
                    print("Momentary Switch")
                else:
                    print(_state(maker, args.human_readable))
            else:
                getattr(maker, state)()
            if args.device != 'all':
                sys.exit(0)

    scan(args, on_switch, on_motion, on_bridge, on_maker)
    # If we got here, we didn't find anything
    print("No device found with that name.")
    sys.exit(1)


def list_(args):
    def on_switch(switch):
        print("Switch:", switch.name)

    def on_motion(motion):
        print("Motion:", motion.name)

    def on_maker(maker):
        print("Maker:", maker.name)

    def on_bridge(bridge):
        print("Bridge:", bridge.name)
        bridge.bridge_get_lights()
        bridge.bridge_get_groups()
        for group in bridge.Groups:
            print("Group:", group)
        for light in bridge.Lights:
            print("Light:", light)

    scan(args, on_switch, on_motion, on_bridge, on_maker)


def status(args):
    def on_switch(switch):
        print("Switch:", switch.name, '\t', _state(switch, args.human_readable))

    def on_motion(motion):
        print("Motion:", motion.name, '\t', _state(motion, args.human_readable))

    def on_maker(maker):
        if maker.switch_mode:
            print("Maker:", maker.name, '\t', "Momentary State:", _state(maker, args.human_readable))
        else:
            print("Maker:", maker.name, '\t', "Persistent State:", _state(maker, args.human_readable))
        if maker.has_sensor:
            if args.human_readable:
                if maker.sensor_state:
                    sensorstate = 'Sensor not triggered'
                else:
                    sensorstate = 'Sensor triggered'
                print('\t\t\t', "Sensor:", sensorstate)
            else:
                print('\t\t\t', "Sensor:", maker.sensor_state)
        else:
            print('\t\t\t' "Sensor not present")

    def on_bridge(bridge):
        print("Bridge:", bridge.name, '\t', _state(bridge, args.human_readable))
        bridge.bridge_get_lights()
        for light in bridge.Lights:
            print("Light:", light, '\t', bridge.light_get_state(bridge.Lights[light]))
        for group in bridge.Groups:
            print("Group:", group, '\t', bridge.group_get_state(bridge.Groups[group]))

    scan(args, on_switch, on_motion, on_bridge, on_maker)


def server(args):
    try:
        from socketio.server import SocketIOServer
        from ouimeaux.server import app, initialize
    except ImportError:
        print("ouimeaux server dependencies are not installed. Please run, e.g., 'pip install ouimeaux[server]'")
        sys.exit(1)
    initialize(bind=getattr(args, 'bind', None))
    level = logging.INFO
    if getattr(args, 'debug', False):
        level = logging.DEBUG
    logging.basicConfig(level=level)
    try:
        # TODO: Move this to configuration
        listen = WemoConfiguration().listen or '0.0.0.0:5000'
        try:
            host, port = listen.split(':')
        except Exception:
            print("Invalid bind address configuration:", listen)
            sys.exit(1)
        SocketIOServer((host, int(port)), app,
                       policy_server=False,
                       namespace="socket.io").serve_forever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)


def wemo():
    import ouimeaux.utils
    ouimeaux.utils._RETRIES = 0

    parser = argparse.ArgumentParser()

    parser.add_argument("-b", "--bind", default=None,
                        help="ip:port to which to bind the response server."
                             " Default is localhost:54321")
    parser.add_argument("-d", "--debug", action="store_true", default=False,
                        help="Enable debug logging")
    parser.add_argument("-e", "--exact-match", action="store_true",
                        default=False,
                        help="Disable fuzzy matching for device names")
    parser.add_argument("-v", "--human-readable", dest="human_readable",
                        action="store_true", default=False,
                        help="Print statuses as human-readable words")
    parser.add_argument("-t", "--timeout", type=int, default=5,
                        help="Time in seconds to allow for discovery")
    subparsers = parser.add_subparsers()

    statusparser = subparsers.add_parser("status",
                                         help="Print status of WeMo devices")
    statusparser.set_defaults(func=status)

    stateparser = subparsers.add_parser("switch",
                                        help="Turn a WeMo Switch on or off")
    stateparser.add_argument("device", help="Name or alias of the device")
    stateparser.add_argument("state", help="'on' or 'off'")
    stateparser.set_defaults(func=switch)

    makerparser = subparsers.add_parser("maker",
                                        help="Get sensor or switch state of a Maker or Turn on or off")
    makerparser.add_argument("device", help="Name or alias of the device")
    makerparser.add_argument("state", help="'on' or 'off' or 'toggle' or 'sensor' or 'switch'")
    makerparser.set_defaults(func=maker)

    stateparser = subparsers.add_parser("light",
                                        help="Turn a WeMo LED light on or off")
    stateparser.add_argument("name", help="Name or alias of the device or group")
    stateparser.add_argument("state", help="'on' or 'off'")
    stateparser.add_argument("dim", nargs='?', type=int,
                             help="Dim value 0 to 255")
    stateparser.set_defaults(func=light)

    listparser = subparsers.add_parser("list",
                                       help="List all devices found in the environment")
    listparser.set_defaults(func=list_)

    serverparser = subparsers.add_parser("server",
                                         help="Run the API server and web app")
    serverparser.set_defaults(func=server)

    args = parser.parse_args()

    if getattr(args, 'debug', False):
        logging.basicConfig(level=logging.DEBUG)

    args.func(args)
