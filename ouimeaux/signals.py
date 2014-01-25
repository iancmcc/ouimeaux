from pysignals import Signal


device_discovered = Signal(providing_args=["address", "headers"])
