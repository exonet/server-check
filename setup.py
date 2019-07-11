#!/usr/bin/env python
import os.path
from setuptools import setup, find_packages

here = os.path.dirname(__file__)
readme = open(os.path.join(here, 'README.rst')).read()

setup(
    name='server_check',
    use_scm_version=True,
    maintainer="Rick van den Hof",
    maintainer_email='support@exonet.nl',
    url='https://github.com/exonet/server-check',
    description='Check a DirectAdmin server to see if all components are operating correctly',
    long_description=readme,
    license='MIT',
    keywords='DirectAdmin check pop3 imap ftp smtp phpmyadmin mod_ruid2 spamassasassin roundcube',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Utilities',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta'
    ],
    setup_requires=['setuptools_scm'],
    install_requires=['mysql-connector', 'requests', 'argparse'],
    packages=find_packages(exclude=['tests', 'tests.*']),
    test_suite='nose.collector',
    entry_points={'console_scripts': ['server_check = server_check:main']},
)
