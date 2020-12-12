# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import pysyslogclient, sys

long_description=open("README", "r").read(4096)

setup(
	name="pysyslogclient",
	version=pysyslogclient.version,
	description='Syslog client implementation (RFC 3164/RFC 5424) with message transfer from RFC 6587 (Syslog over TCP)',
	long_description='Originally forked from syslog client of Alexander Böhm, https://github.com/aboehm/pysyslogclient'.
	license='BSD-2-Clause',
	url="https://github.com/maciejbudzyn/syslog-py",
	
	author="Maciej Budzyński",
	author_email="maciej.budzyn@gmail.com",

	classifiers = [
		'Development Status :: 5 - Production/Stable',

		'License :: OSI Approved :: BSD License',

		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',

		'Operating System :: Unix',
		'Operating System :: POSIX :: Linux',
		'Operating System :: Microsoft',

		'Topic :: System :: Logging',
		'Topic :: System :: Monitoring',
  ],

	packages=find_packages(),

	keywords="syslog logging monitoring",
)

# vim: ft=python tabstop=2 shiftwidth=2 noexpandtab :
