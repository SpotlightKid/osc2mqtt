#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# setup.py - Setup file for the osc2mqtt project.
#
"""An OSC to MQTT bridge based on pyliblo and paho.mqtt."""

from io import open
from setuptools import setup

# Add custom distribution meta-data, avoids warning when running setup
from distutils.dist import DistributionMetadata
DistributionMetadata.repository = None

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Intended Audience :: Manufacturing
Intended Audience :: Other Audience
License :: OSI Approved :: MIT License
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: MacOS :: MacOS X
Programming Language :: Python
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Topic :: Communications
Topic :: Internet
Topic :: Home Automation
Topic :: Multimedia :: Sound/Audio
"""
name = 'osc2mqtt'
url = 'https://github.com/SpotlightKid/%s' % name.lower()

setup(
    name = name,
    version = '0.1b1',
    description = __doc__.splitlines()[0],
    long_description = open('README.md', encoding='utf-8').read(),
    keywords = 'osc mqtt iot',
    classifiers = [c.strip() for c in classifiers.splitlines()
        if c.strip() and not c.startswith('#')],
    author = 'Christopher Arndt',
    author_email = 'chris@chrisarndt.de',
    url = url,
    repository = 'https://github.com/SpotlightKid/%s' % name.lower(),
    download_url = url + '/releases',
    license = 'MIT License',
    platforms = 'POSIX, Windows, MacOS X',
    py_modules = ['osc2mqtt'],
    install_requires = [
        'paho.mqtt',
        'pyliblo',
    ],
    entry_points = {
        'console_scripts': [
            'osc2mqtt = osc2mqtt:main'
        ]
    },
    zip_safe = True
)
