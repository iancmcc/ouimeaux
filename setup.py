from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='ouimeaux',
      version=version,
      description="Python API to Belkin WeMo devices",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Ian McCracken',
      author_email='ian.mccracken@gmail.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      dependency_links = [
          'https://github.com/downloads/SiteSupport/gevent/gevent-1.0rc2.tar.gz#egg=gevent-1.0.rc2'
      ],
      install_requires=[
          'gevent >= 1.0rc2',
          'requests'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
