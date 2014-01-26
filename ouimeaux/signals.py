from pysignals import Signal, receiver

# Work around a bug in pysignals when in the interactive interpreter
import sys
_main = sys.modules.get('__main__')
if _main:
    _main.__file__ = "__main__.py"


# Fires when a device responds to a broadcast 
discovered = Signal(providing_args=["address", "headers"])

# Fires when a device is found and added to the environment
devicefound = Signal()

# Fires when a subscriber receives an event
subscription = Signal(providing_args=["type", "value"])

# Fires when a device changes state
statechange = Signal(providing_args=["state"])


@receiver(subscription)
def _got_subscription(sender, **kwargs):
    if kwargs['type'] == 'BinaryState':
        statechange.send(sender, state=int(kwargs['value']))
