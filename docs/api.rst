===========
Python API
===========

Environment
-----------
The main interface is presented by an ``Environment``, which optionally accepts
functions called when a Switch or Motion device is identified::

    >>> from ouimeaux.environment import Environment
    >>>
    >>> def on_switch(switch):
    ...     print "Switch found!", switch.name
    ...
    >>> def on_motion(motion):
    ...     print "Motion found!", motion.name
    ...
    >>> env = Environment(on_switch, on_motion)

Start up the server to listen for responses to the discovery broadcast::

    >>> env.start()

Discovery of all WeMo devices in an environment is then straightforward; simply
pass the length of time (in seconds) you want discovery to run::

    >>> env.discover(seconds=3)
    Switch found! Living Room

During that time, the ``Environment`` will continually broadcast search requests
and parse responses. At any point, you can see the names of discovered devices::

    >>> env.list_switches()
    ['Living Room', 'TV Room', 'Front Closet']
    >>> env.list_motions()
    ['Front Hallway']

Devices can be retrieved by using ``get_switch`` and ``get_motion`` methods::

    >>> switch = env.get_switch('TV Room')
    >>> switch
    <WeMo Switch "TV Room">

Devices
-------
All devices have an ``explain()`` method, which will print out a list of all
available services, as well as the actions and arguments to those actions
on each service::

    >>> switch.explain()

    basicevent
    ----------
      SetSmartDevInfo(SmartDevURL)
      SetServerEnvironment(ServerEnvironmentType, TurnServerEnvironment, ServerEnvironment)
      GetDeviceId()
      GetRuleOverrideStatus(RuleOverrideStatus)
      GetIconURL(URL)
      SetBinaryState(BinaryState)
    ...

Services and actions are available via simple attribute access. Calling actions
returns a dictionary of return values::

    >>> switch.basicevent.SetBinaryState(BinaryState=0)
    {'BinaryState': 0}

Events
------
.. warning:: This events framework is deprecated and will be removed prior to the 1.0 release. Please use the signals framework.

By default, ouimeaux subscribes to property change events on discovered
devices (this can be disabled by passing ``with_subscribers=False`` to the
``Environment`` constructor). You can register callbacks that will be called
when switches and motions change state (on/off, or motion detected)::

    >>> def on_motion(value):
    ...     print "Motion detected!"
    ...
    >>> env.get_motion('Front Hallway').register_listener(on_motion)
    >>> env.wait(timeout=60)

Note the use of ``Environment.wait()`` to give control to the event loop for
events to be detected. A timeout in seconds may optionally be specified;
default is no timeout.

Signals
-------
A simple signals framework (using pysignals_) is included to replace the
rudimentary events in earlier releases. These are found in the
`ouimeaux.signals` module. Signal handlers may be registered using the
``receiver`` decorator and must have the signature ``sender, **kwargs``::

    @receiver(devicefound)
    def handler(sender, **kwargs):
        print "Found device", sender


Where ``sender`` is the relevant object (in most cases, the device). Signals
may also have handlers registered using ``signal.connect(handler)``::

    def handler(sender, **kwargs):
        pass

    statechange.connect(sender)

Available signals:

    ``discovered``
        Fires when a device responds to the broadcast request. Includes:
         - ``sender``: The UPnP broadcast component
         - ``address``: The address of the responding device
         - ``headers``: The response headers

    ``devicefound``
        Sent when a device is found and registered into the environment. Includes:
         - ``sender``: The device found

    ``subscription``
        Sent when a device sends an event as the result of a subscription. Includes:
         - ``sender``: The device that sent the event
         - ``type``: The type of the event send (e.g., ``BinaryState``)
         - ``value``: The value associated with the event

    ``statechange``
        Sent when a device indicates it has detected a state change. Includes:
         - ``sender``: The device that changed state
         - ``state``: The resulting state (0 or 1)


See the pysignals_ documentation for further information.

Example: Registering a handler for when a Light Switch switches on or off::

    from ouimeaux.signals import statechange, receiver

    env = Environment(); env.start()
    env.discover(5)

    switch = env.get_switch('Porch Light')

    @receiver(statechange, sender=switch)
    def switch_toggle(device, **kwargs):
        print device, kwargs['state']

    env.wait()  # Pass control to the event loop

See the examples_ for a more detailed implementation.

.. _pysignals: https://github.com/theojulienne/PySignals

Switches
--------
Switches have three shortcut methods defined: ``get_state``, ``on`` and
``off``. Switches also have a ``blink`` method, which accepts a number of
seconds. This will toggle the device, wait the number of seconds, then toggle
it again. Remember to call ``env.wait()`` to give control to the event loop.

Motions
-------
Motions have one shortcut method defined: ``get_state``.

Insight
-------
In addition to the normal Switch methods, Insight switches have several metrics
exposed::

    insight.today_kwh
    insight.current_power
    insight.today_ontime
    insight.on_for
    insight.in_standby_since
    insight.today_standby_time

Device Cache
------------
By default, device results are cached on the filesystem for quicker
initialization. This can be disabled by passing ``with_cache=False`` to the
``Environment`` constructor. On a related note, if you want to use the cache
exclusively, you can pass ``with_discovery=False`` to the ``Environment``
constructor to disable M-SEARCH requests.

You can clear the device cache either by deleting the file ``~/.wemo/cache`` 
or by using the ``wemo clear`` command.

Examples
--------
Detailed examples_ are included in the source demonstrating common use cases.
Suggestions (or implementations) for more are always welcome.

.. _examples: https://github.com/iancmcc/ouimeaux/tree/develop/ouimeaux/examples