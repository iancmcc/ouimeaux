========
ouimeaux
========

ouimeaux is a Python interface to `Belkin WeMo`_ devices. It uses gevent_
for async I/O and requests_ for communication with the devices. It also
provides a minimal command-line interface for discovery and switch toggling.

Currently supported devices include Motions, Switches and Light Switches.

.. contents::
   :depth: 3

Python API
~~~~~~~~~~

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

Switches
--------
Switches have three shortcut methods defined: ``get_state``, ``on`` and ``off``.

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

Configuration
-------------
A configuration file in YAML format will be created at ~/.wemo/config.yml::

    # ip:port to bind to when receiving responses from discovery.
    # The default is first DNS resolution of local host, port 54321
    #
    # bind: 10.1.2.3:9090

    # Whether to use a device cache (stored at ~/.wemo/cache)
    #
    # cache: false

    aliases:
    # Shortcuts to longer device names. Uncommenting the following
    # line will allow you to execute 'wemo switch lr on' instead of
    # 'wemo switch "Living Room Lights" on'
    #
    #    lr: Living Room Lights

Command Line
~~~~~~~~~~~~
The ``wemo`` script will discover devices in your environment and turn
switches on and off. To list devices::

    $ wemo list

Default is to search for 5 seconds; you can pass ``--timeout`` to change that.

You can also print the status of every device found in your environment (the
``-v`` option is available to print on/off instead of 0/1)::

    $ wemo status

To turn a switch on and off, you first have to know the name. Then::

    $ wemo switch "TV Room" on
    $ wemo switch "TV Room" off

You can also toggle the device::

    $ wemo switch "TV Room" toggle

Or check its current status (the ``-v`` option will print the word on/off
instead of 0/1)::

    $ wemo -v switch "TV Room" status
    on

The ``wemo`` script will do fuzzy matching of the name you pass in (this can be
disabled with the ``-e`` option)::

    $ wemo switch tvrm on

Aliases configured in the file will be accessible on the command line as well::

    aliases:
        tv: TV Room Lights

    $ wemo switch tv on

Note: If an alias is used on the command line, fuzzy matching will not be
attempted.

You can also clear the device cache from the command line::
    
    $ wemo clear

The ``wemo`` script will obey configured settings; they can also be overridden
on the command line:

``-b``, ``--bind IP:PORT``
    Bind to this host and port when listening for responses

``-d``, ``--debug``
    Enable debug logging to stdout

``-e``, ``--exact-match``
    Disable fuzzy matching

``-f``, ``--no-cache``
    Disable the device cache

``-v``, ``--human-readable``
    Print statuses as human-readable words



Installation
~~~~~~~~~~~~

Linux
-----
ouimeaux requires Python header files to build some dependencies, and is
installed normally using pip or easy_install.

Debian/Ubuntu::

    sudo apt-get install python-setuptools python-dev
    sudo easy_install pip
    sudo pip install ouimeaux

RHEL/CentOS/Fedora::

    sudo yum -y install python-setuptools python-devel
    sudo easy_install pip
    sudo pip install ouimeaux

If you wish to build from a local copy of the source, you can of course always
execute::

    sudo python setup.py install

Windows
-------
ouimeaux requires gevent version 1.0rc2 or higher. If you don't have the 
ability to compile gevent and greenlet (a sub-dependency) locally, you can 
find and download the binary installers for these packages here:

- gevent: https://github.com/SiteSupport/gevent/downloads
- greenlet: https://pypi.python.org/pypi/greenlet

Changelog
~~~~~~~~~

Release 0.5.3 (January 25, 2014)
--------------------------------
- Fixed #20: Allow timeout in environment.wait()
- Fixed #21: Add Insight support

Release 0.5.2 (November 23, 2013)
---------------------------------
- Fixed #14: Indicate Connection:close header to avoid logging when WeMo sends
  invalid HTTP response.

Release 0.5.1 (November 9, 2013)
--------------------------------
- Fixed #10: Updated subscriber listener to use more reliable method of
  retrieving non-loopback IP address; updated docs to fix typo in listener
  registration example (thanks to @benhoyle, @francxk)
- Fixed #11: Remove instancemethod objects before attempting to pickle devices
  in the cache (thanks @piperde, @JonPenner, @tomtomau, @masilu77)

Release 0.5 (October 14, 2013)
-------------------------------
- Added fuzzy matching of device name when searching/toggling from command line
- Added ``status`` mode to print status for all devices
- Added ``switch status`` mode to print status for specific device
- Added flags for all command-line options
- Fixed #9: Removed unused fcntl import that precluded Windows usage (thanks to
  @deepseven)

Release 0.4.3 (August 31, 2013)
-------------------------------
- Used new method of obtaining local IP for discovery that is less likely to
  return loopback
- Exit with failure and instructions for solution if loopback IP is used
- Updated installation docs to include python-dev and pip instructions (patch
  by @fnaard)
- Fixed README inclusion bug that occasionally broke installation via pip.
- Added ``--debug`` option to enable debug logging to stdout

Release 0.4 (August 17, 2013)
-----------------------------
- Fixed #7: Added support for light switch devices (patch by nschrenk).
- Fixed #6: Added "wemo clear" command to clear the device cache.

Release 0.3 (May 25, 2013)
--------------------------
- Fixed #4: Added ability to specify ip:port for discovery server binding. Removed
  documentation describing need to disable SSDP service on Windows.
- Fixed #5: Added device cache for faster results.
- Added configuration file.
- Added ability to configure aliases for devices to avoid quoting strings on
  the command line.
- Added 'toggle' command to command line switch control.

Release 0.2 (April 21, 2013)
------------------------------
- Fixed #1: Added ability to subscribe to motion and switch state change events.
- Added Windows installation details to README (patch by @brianpeiris)
- Cleaned up UDP server lifecycle so rediscovery doesn't try to start it back up.

Release 0.1 (February 2, 2013)
------------------------------
- Initial release.


.. _gevent: http://www.gevent.org/
.. _requests: http://docs.python-requests.org/en/latest/
.. _Belkin WeMo: http://www.belkin.com/us/wemo
