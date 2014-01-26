============
Installation
============

Basic
-----
At the command line::

    $ easy_install ouimeaux

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv ouimeaux
    $ pip install ouimeaux

Linux
-----
ouimeaux requires Python header files to build some dependencies, and is
installed normally using pip or easy_install.

Debian/Ubuntu::

    sudo apt-get install python-setuptools python-dev

RHEL/CentOS/Fedora::

    sudo yum -y install python-setuptools python-devel

If you wish to build from a local copy of the source, you can of course always
execute::

    python setup.py install


Windows
-------
ouimeaux requires gevent version 1.0rc2 or higher. If you don't have the 
ability to compile gevent and greenlet (a sub-dependency) locally, you can 
find and download the binary installers for these packages here:

- gevent: https://github.com/SiteSupport/gevent/downloads
- greenlet: https://pypi.python.org/pypi/greenlet
