=============
Configuration
=============

A configuration file in YAML format will be created at ``~/.wemo/config.yml``::

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

    # Web app bind address
    #
    # listen: 0.0.0.0:5000

    # Require basic authentication (username:password) for the web app
    #
    # auth: admin:password
