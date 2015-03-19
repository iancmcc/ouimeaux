#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

here = lambda *a: os.path.join(os.path.dirname(__file__), *a)


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open(here('README.rst')).read()
history = open(here('HISTORY.rst')).read().replace('.. :changelog:', '')
requirements = [x.strip() for x in open(here('requirements.txt')).readlines()]

setup(
    name='ouimeaux',
    version='0.7.9',
    description='Open source control for Belkin WeMo devices',
    long_description=readme + '\n\n' + history,
    author='Ian McCracken',
    author_email='ian.mccracken@gmail.com',
    url='https://github.com/iancmcc/ouimeaux',
    packages=[
        'ouimeaux',
    ],
    package_dir={'ouimeaux': 'ouimeaux'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='ouimeaux',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Home Automation',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    entry_points={
        'console_scripts': [
            'wemo = ouimeaux.cli:wemo'
        ]
    },
    test_suite='tests',
)