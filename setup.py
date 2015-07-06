#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = __import__('balancer').__version__

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

description = "A set of tools for using Django's multi-db feature to balance "
description += "database requests"

setup(
    name='django-balancer',
    version=VERSION,
    description=description,
    long_description = long_description,
    author='Brandon Konkle, Mike Helmick',
    author_email='mike@drund.com',
    license='License :: OSI Approved :: BSD License',
    url='http://github.com/michaelhelmick/django-balancer',
    packages=['balancer'],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
    ]
)
