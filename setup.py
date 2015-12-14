#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from setuptools.command.test import test as TestCommand
from setuptools import find_packages
import uuid
import imp

from pip.req import parse_requirements

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()

ps_meta = imp.load_source('_meta', 'public_search/__meta__.py')

packages = find_packages()

install_requires = parse_requirements('requirements/base.txt', session=uuid.uuid1())
tests_require = parse_requirements('requirements/dev.txt', session=uuid.uuid1())

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Debuggers',
    'Topic :: Software Development :: Libraries :: Python Modules',
]



setup(
    name='public-search',
    version=ps_meta.__version__,
    description='Ambry Public Search Web Application',
    long_description=readme,
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    install_requires=[x for x in reversed([str(x.req) for x in install_requires])],
    tests_require=[x for x in reversed([str(x.req) for x in tests_require])],
    scripts=['scripts/run-public-search.sh'],
    author=ps_meta.__author__,
    author_email='eric@civicknowledge.com',
    url='https://github.com/CivicKnowledge/public-search.git',
    license='MIT',
    classifiers=classifiers
)
