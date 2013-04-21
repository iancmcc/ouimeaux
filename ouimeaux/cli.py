import sys
from argparse import ArgumentParser

from .environment import Environment


def wemo():
    parser = ArgumentParser()

    parser.add_argument("--timeout", type=int, default=5,
                        help="Time in seconds to allow for discovery")
    subparsers = parser.add_subparsers()

    stateparser = subparsers.add_parser("switch",
                                        help="Turn a WeMo Switch on or off")
    stateparser.add_argument("device", help="Name of the device")
    stateparser.add_argument("state", help="'on' or 'off")

    subparsers.add_parser("list",
                          help="List all devices found in the environment")

    args = parser.parse_args()

    ls = state = None

    if getattr(args, 'device', None):
        if args.state.lower() in ("on", "1", "true"):
            state = "on"
        elif args.state.lower() in ("off", "0", "false"):
            state = "off"
    else:
        ls = True

    def on_switch(switch):
        if state:
            if switch.name == args.device:
                getattr(switch, state)()
                sys.exit(0)
        elif ls:
            print "Switch: ", switch.name

    def on_motion(motion):
        if ls:
            print "Motion: ", motion.name

    try:
        env = Environment(on_switch, on_motion, with_subscribers=False)
        env.start()
        env.discover(args.timeout)
    except KeyboardInterrupt:
        sys.exit(0)

    if not ls:
        print "No device found with that name."
        sys.exit(1)

