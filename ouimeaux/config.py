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
        with open(filename, 'r') as cfg:
            self._parsed = yaml.load(cfg)

    @property
    def aliases(self):
        return self._parsed.get('aliases', {})

    @property
    def bind(self):
        return self._parsed.get('bind', None)


class Cache(object):
    def __init__(self, shelf):
        self._shelf = shelf

    def add_device(self, device):
        assert isinstance(device, Device)
        print "Adding device"
        d = self._shelf.setdefault('devices', {})
        d[device.name] = device

    @property
    def devices(self):
        return self._shelf.setdefault('devices', {}).itervalues()


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

