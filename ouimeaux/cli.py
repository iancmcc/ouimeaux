import sys
from argparse import ArgumentParser

from .environment import Environment
from ouimeaux.config import get_cache


def wemo():
    parser = ArgumentParser()

    parser.add_argument("--timeout", type=int, default=5,
                        help="Time in seconds to allow for discovery")
    parser.add_argument("--bind", default=None,
                        help="ip:port to which to bind the response server."
                             " Default is localhost:54321")
    parser.add_argument("--no-cache", dest="use_cache", default=None,
                        action="store_false",
                        help="Disable the device cache")
    subparsers = parser.add_subparsers()

    stateparser = subparsers.add_parser("switch",
                                        help="Turn a WeMo Switch on or off")
    stateparser.add_argument("device", help="Name or alias of the device")
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
        elif args.state.lower() == "toggle":
            state = "toggle"
    else:
        ls = True

    def on_switch(switch):
        if state:
            if switch.name == args.device:
                if state == "toggle":
                    found_state = switch.get_state(force_update=True)
                    switch.set_state(not found_state)
                else:
                    getattr(switch, state)()
                sys.exit(0)
        elif ls:
            print "Switch: ", switch.name

    def on_motion(motion):
        if ls:
            print "Motion: ", motion.name

    try:
        env = Environment(on_switch, on_motion, with_subscribers=False,
                          bind=args.bind, with_cache=args.use_cache)
        if getattr(args, 'device', None):
            args.device = env._config.aliases.get(args.device, args.device)
        env.start()
        with get_cache() as c:
            if c.empty:
                args.use_cache = False
        if (args.use_cache is not None and not args.use_cache) or (
                    env._config.cache is not None and not env._config.cache):
            env.discover(args.timeout)
    except KeyboardInterrupt:
        sys.exit(0)

    if not ls:
        print "No device found with that name."
        sys.exit(1)

