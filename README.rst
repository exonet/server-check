.. image:: https://img.shields.io/pypi/v/server-check.svg?style=flat-square
     :alt: PyPi version

.. image:: https://img.shields.io/pypi/pyversions/server-check.svg?style=flat-square
     :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/l/server-check.svg?style=flat-square
     :alt: License

.. image:: https://travis-ci.org/exonet/server-check.svg
  :target: https://travis-ci.org/exonet/server-check
     :alt: Build Status

.. image:: https://coveralls.io/repos/exonet/server-check/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/exonet/server-check?branch=master


server_check
-------------

The goal of this tool is to check a server to see if all components are still operating correctly.
It will check the following:

* PHP: sessions
* PHP: mod_ruid2 (files created with PHP have proper ownership)
* PHP: sending email
* PHP: php -v does not generate errors (all modules could be loaded)
* MySQL: able to login with the password in mysql.conf
* MySQL: able to log in to phpMyAdmin.
* Email: able to connect to dovecot (POP3/IMAP)
* Email: able to connect to exim and deliver a message
* Email: mail should be filtered by SpamAssassin
* Email: able to access roundcube.
* FTP: able to connect, upload and download a file

Requirements
------------
Currently this tool is only supported on DirectAdmin servers.
The tool requires the Python header files and MySQL-python.

Installation
------------
To install this tool on a DirectAdmin server, make sure you have installed the Python development
package and the Python package manager (pip) for your distribution. If MySQL-python isn't installed
yet, make sure the mysql_config tool is in your $PATH.

To install the latest version::

 pip install server_check

To install on Debian 6/7 based DirectAdmin servers::

 apt-get install python-dev python-pip && PATH=$PATH:/usr/local/mysql/bin pip install server_check

Screenshot
----------
.. image:: https://www.exonet.nl/img/pictures/articles/52/server_check.gif


Conventions
-----------

Code style guide: PEP 8::

 pycodestyle

Testing
-------

Run unit tests and coverage::

 py.test --cov=server_check --cov-report term-missing --cov-fail-under=95 tests/

Security
--------

If you discover any security related issues please email `support@exonet.nl <mailto:support@exonet.nl>`_ instead of using the issue tracker.
