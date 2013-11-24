from setuptools import setup, find_packages
import sys, os

version = '0.5.2'

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    description = f.read()

setup(name='ouimeaux',
      version=version,
      description="Python API to Belkin WeMo devices",
      long_description=description,
      classifiers=[
          "License :: OSI Approved :: BSD License",
          "Topic :: Home Automation",
          "Programming Language :: Python"
      ], 
      keywords='belkin wemo soap api homeautomation control',
      author='Ian McCracken',
      author_email='ian.mccracken@gmail.com',
      url='http://github.com/iancmcc/ouimeaux',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      dependency_links = [
          'https://github.com/downloads/surfly/gevent/gevent-1.0rc2.tar.gz#egg=gevent-1.0.rc2'
      ],
      install_requires=[
          'gevent >= 1.0rc2',
          'requests',
          'pyyaml'
      ],
      entry_points={
          'console_scripts': [
              'wemo = ouimeaux.cli:wemo'
          ]
      },
      )
