#!/usr/bin/env python
version = "1.0"

import codecs
import os
import sys
import pip

from pip.req import parse_requirements
from setuptools import setup, find_packages
from os.path import abspath, dirname, join

here = abspath(dirname(__file__))

# determine the python version
IS_PYPY = hasattr(sys, 'pypy_version_info')

with codecs.open(join(here, 'README.md'), encoding='utf-8') as f:
    README = f.read()

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

install_reqs = parse_requirements('requirements.txt', session=pip.download.PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='server_check',
    version=version,
    maintainer="Rick van den Hof",
    maintainer_email='r.vandenhof@exonet.nl',
    url='https://github.com/exonet/scripts/server_check',
    description='Check a server to see if all components are (still) operating correctly',
    long_description=README,
    license='PRIVATE',
    keywords='',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Utilities',
        'Environment :: Console',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta'
    ],
    setup_requires=reqs,
    install_requires=reqs,
    packages=find_packages(exclude=['tests', 'tests.*']),
    test_suite='nose.collector',
    entry_points={'console_scripts': ['server_check = server_check.server_check:main']},
)
