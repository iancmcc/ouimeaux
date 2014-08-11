from contextlib import contextmanager, closing
import os
import shelve
import gevent
from gevent.lock import RLock

import yaml
from ouimeaux.device import Device


def in_home(*path):
    try:
        from win32com.shell import shellcon, shell
    except ImportError:
        home = os.path.expanduser("~")
    else:
        home = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
    return os.path.join(home, *path)


def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


class WemoConfiguration(object):
    def __init__(self, filename=None):
        if filename is None:
            ensure_directory(in_home('.wemo'))
            filename = in_home('.wemo', 'config.yml')
        if not os.path.isfile(filename):
            with open(filename, 'w') as f:
                f.write("""
aliases:
# Shortcuts to longer device names. Uncommenting the following
# line will allow you to execute 'wemo switch lr on' instead of
# 'wemo switch "Living Room Lights" on'
#
#    lr: Living Room Lights

# ip:port to bind to when receiving responses from discovery.
# The default is first DNS resolution of local host, port 54321
#
# bind: 10.1.2.3:9090

# Whether to use a device cache (stored at ~/.wemo/cache)
#
# cache: true

# Web app bind address
#
# listen: 0.0.0.0:5000
""")
        with open(filename, 'r') as cfg:
            self._parsed = yaml.load(cfg)

    @property
    def aliases(self):
        return self._parsed.get('aliases') or {}

    @property
    def bind(self):
        return self._parsed.get('bind', None)

    @property
    def cache(self):
        return self._parsed.get('cache', None)

    @property
    def listen(self):
        return self._parsed.get('listen', None)


class Cache(object):
    def __init__(self, shelf):
        self._shelf = shelf

    @property
    def empty(self):
        return not self._shelf.get('devices')

    def clear(self):
        self._shelf.clear()

    def add_device(self, device):
        assert isinstance(device, Device)
        d = self._shelf.setdefault('devices', {})
        d[device.name] = device

    def invalidate(self, device):
        assert isinstance(device, Device)
        d = self._shelf.setdefault('devices', {})
        d.pop(device.name)
        self._shelf.clear()
        self._shelf['devices'] = d

    @property
    def devices(self):
        try:
            return self._shelf.setdefault('devices', {}).itervalues()
        except ImportError:
            self._shelf.clear()
            return self.devices


_CACHE_LOCK = RLock()

@contextmanager
def get_cache():
    ensure_directory(in_home('.wemo'))
    filename = in_home('.wemo', 'cache')
    _CACHE_LOCK.acquire(blocking=True)
    try:
        with closing(shelve.open(filename, writeback=True)) as cache:
            yield Cache(cache)
    finally:
        _CACHE_LOCK.release()

