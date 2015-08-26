import os
from requests import Session
import pytest
import collections
from server_check import directadmin
from mock import Mock
import pwd

DomainInfo = collections.namedtuple('DomainInfo', 'domain, user, password')


@pytest.fixture(scope='module')
def domain():
    return DomainInfo('foobar.nl', 'foobar', '123456')
