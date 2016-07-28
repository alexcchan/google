#!/usr/bin/python

from distutils.core import setup

setup(
	# Basic package information.
	name = 'google',
	version = '0.0.0',
	packages = ['google'],
	include_package_data = True,
	install_requires = ['httplib2', 'gdata', 'google-api-python-client', 'oauth2client', 'simplejson',],
	license='LICENSE.txt',
	url = 'https://github.com/alexcchan/google/tree/master',
	keywords = 'google api',
	description = 'Google API Wrapper for Python',
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: Apache Software License',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Internet'
	],
)


