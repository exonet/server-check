server\_check
=============

The goal of this tool is to check a server to see if all components are still operating correctly.
It will check the following:

* PHP sessions
* PHP: mod\_ruid2 (files created with PHP have proper ownership)
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
