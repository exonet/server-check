# apt-get install python-requests
import requests
from exceptions import TestException


def test_roundcube():
    r = requests.get('http://localhost/roundcube/')
    if r.status_code == 200 and "Roundcube Webmail Login" in r.text:
        return "Roundcube accessible"
    else:
        raise TestException("String 'Roundcube Webmail Login' not found at http://localhost/roundcube/")
