import requests
from exceptions import TestException


def test_roundcube(url='http://localhost/roundcube/'):
    r = requests.get(url)
    if r.status_code == 200 and "Roundcube Webmail" in r.text:
        return "Roundcube accessible"
    else:
        raise TestException("String 'Roundcube Webmail' not found at %s" % url)
