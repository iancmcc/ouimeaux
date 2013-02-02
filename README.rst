========
ouimeaux
========

ouimeaux is a Python interface to `Belkin WeMo`_ devices. It uses gevent_
for async I/O and requests_ for communication with the devices.

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
    ...     print "Motion found!", switch.motion
    ...
    >>> env = Environment(on_switch, on_motion)

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

Switches
--------
Switches have two shortcut methods defined, ``on()`` and ``off()``.

Motions
-------
Motions currently don't have any shortcut methods defined.


.. _gevent: http://www.gevent.org/
.. _requests: http://docs.python-requests.org/en/latest/
.. _Belkin WeMo: http://www.belkin.com/us/wemo
