# apt-get install python-requests
import requests
from exceptions import TestException


def test_phpmyadmin(session=requests.Session()):
    # Read MySQL username and password from /usr/local/directadmin/conf/mysql.conf
    user = ""
    passwd = ""
    with open('/usr/local/directadmin/conf/mysql.conf', 'r') as fh:
        for line in fh:
            # user=xxx
            # passwd=xxxx
            key, value = line.strip().split('=')
            if key == 'user':
                user = value
            elif key == 'passwd':
                passwd = value

    r = session.get('http://localhost/phpmyadmin/', auth=(user, passwd))
    if r.status_code == 200 and "User: %s@localhost" % user in r.text:
        return "Logged in and authenticated"
    else:
        raise TestException("Unable to log in to phpMyAdmin with the '%s' user." % user)
