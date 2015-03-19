================
``wemo`` Command
================

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

WeMo LED Bulbs are supported on the command line as well. Control them like
switches with ``wemo light``::

    $ wemo light lamp on

Or set them to a dimness level from 1 to 255::

    $ wemo light lamp on 45

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