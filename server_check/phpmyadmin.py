# apt-get install python-requests
import requests
from bcolors import ok, error


def test_phpmyadmin():
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

    r = requests.get('http://localhost/phpmyadmin/', auth=(user + "a", passwd))
    if r.status_code == 200 and "User: %s@localhost" % user in r.text:
        ok("Logged in and authenticated")
    else:
        error("Unable to log in to phpMyAdmin with the '%s' user." % user)
