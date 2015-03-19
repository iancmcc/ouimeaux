.. :changelog:

History
-------

Release 0.7.9 (March 17, 2015)
++++++++++++++++++++++++++++++
- Command line support for WeMo LED Light (thanks @fritz-fritz)
- Command line support for WeMo Maker (thanks @logjames)
- Support for 2.0.0 firmware (thanks @fritz-fritz)
- Bug fixes

Release 0.7.3 (August 10, 2014)
++++++++++++++++++++++++++++++++
- Fixed #18: Error when run as root
- Fixed #26: Evict devices from cache when unreachable
- Fixed #29: GetPower stopped working for Insight devices
- Fixed #31: Add blink method on switches, include in REST API
- Fixed #33, #37: Handle invalid devices without dying
- Fixed #35: Require requests >= 2.3.0
- Fixed #40: Retry requests in the event of failure
- Fixed #47: Don't choke on invalid newlines in XML returned by switches
             (thanks to @fingon)

Release 0.7.2 (January 28, 2014)
++++++++++++++++++++++++++++++++
- Fix a bug with using query parameters on /api/device

Release 0.7 (January 27, 2014)
++++++++++++++++++++++++++++++
- Added REST API
- Added Web app

Release 0.6 (January 25, 2014)
++++++++++++++++++++++++++++++++
- Added signals framework
- Fixed #16, #19, #22: Defensively resubscribe to events when device responds with an error
- Fixed #15: Signals framework includes relevant device when sending signal
- Refactored structure, added Sphinx docs

Release 0.5.3 (January 25, 2014)
++++++++++++++++++++++++++++++++
- Fixed #20: Allow timeout in environment.wait()
- Fixed #21: Add Insight support

Release 0.5.2 (November 23, 2013)
+++++++++++++++++++++++++++++++++
- Fixed #14: Indicate Connection:close header to avoid logging when WeMo sends
  invalid HTTP response.

Release 0.5.1 (November 9, 2013)
++++++++++++++++++++++++++++++++
- Fixed #10: Updated subscriber listener to use more reliable method of
  retrieving non-loopback IP address; updated docs to fix typo in listener
  registration example (thanks to @benhoyle, @francxk)
- Fixed #11: Remove instancemethod objects before attempting to pickle devices
  in the cache (thanks @piperde, @JonPenner, @tomtomau, @masilu77)

Release 0.5 (October 14, 2013)
+++++++++++++++++++++++++++++++
- Added fuzzy matching of device name when searching/toggling from command line
- Added ``status`` mode to print status for all devices
- Added ``switch status`` mode to print status for specific device
- Added flags for all command-line options
- Fixed #9: Removed unused fcntl import that precluded Windows usage (thanks to
  @deepseven)

Release 0.4.3 (August 31, 2013)
+++++++++++++++++++++++++++++++
- Used new method of obtaining local IP for discovery that is less likely to
  return loopback
- Exit with failure and instructions for solution if loopback IP is used
- Updated installation docs to include python-dev and pip instructions (patch
  by @fnaard)
- Fixed README inclusion bug that occasionally broke installation via pip.
- Added ``--debug`` option to enable debug logging to stdout

Release 0.4 (August 17, 2013)
+++++++++++++++++++++++++++++
- Fixed #7: Added support for light switch devices (patch by nschrenk).
- Fixed #6: Added "wemo clear" command to clear the device cache.

Release 0.3 (May 25, 2013)
++++++++++++++++++++++++++
- Fixed #4: Added ability to specify ip:port for discovery server binding. Removed
  documentation describing need to disable SSDP service on Windows.
- Fixed #5: Added device cache for faster results.
- Added configuration file.
- Added ability to configure aliases for devices to avoid quoting strings on
  the command line.
- Added 'toggle' command to command line switch control.

Release 0.2 (April 21, 2013)
++++++++++++++++++++++++++++++
- Fixed #1: Added ability to subscribe to motion and switch state change events.
- Added Windows installation details to README (patch by @brianpeiris)
- Cleaned up UDP server lifecycle so rediscovery doesn't try to start it back up.

Release 0.1 (February 2, 2013)
++++++++++++++++++++++++++++++
- Initial release.

* First release on PyPI.