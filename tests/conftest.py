import os
from requests import Session
import pytest
import collections
from server_check import directadmin
from mock import Mock
import pwd

DomainInfo = collections.namedtuple('DomainInfo', 'domain, user, password')


@pytest.fixture(scope='module')
def session():
    # Mock a fake session
    mockSession = Mock(spec=Session())
    postreturn = collections.namedtuple('post', 'text, status_code')
    postreturn.text = "error=0"
    sessionSpec = {'post.return_value': postreturn}
    mockSession.configure_mock(**sessionSpec)

    return mockSession


@pytest.fixture(scope='module')
def mockpwd():
    mockpwd = Mock(spec=pwd)
    pwdSpec = {'getpwnam.return_value': ['', 0, 0, 0]}
    mockpwd.configure_mock(**pwdSpec)
    return mockpwd


@pytest.fixture(scope='module')
def domain(session):

    domain, user, password = directadmin.create_random_domain("", "", session)

    # make sure the public_html directory exists
    if not os.path.isdir("/home/%s/domains/%s/public_html" % (user, domain)):
        os.makedirs("/home/%s/domains/%s/public_html" % (user, domain))

    return DomainInfo(domain, user, password)
