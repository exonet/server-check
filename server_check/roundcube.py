# apt-get install python-requests
import requests
from exceptions import TestException


def test_roundcube(url='http://localhost/roundcube/'):
    r = requests.get(url)
    if r.status_code == 200 and "Roundcube Webmail Login" in r.text:
        return "Roundcube accessible"
    else:
        raise TestException("String 'Roundcube Webmail Login' not found at %s" % url)
