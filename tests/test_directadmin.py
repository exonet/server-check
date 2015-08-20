from betamax import Betamax
from requests import Session
import pytest
import collections

with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'

DomainInfo = collections.namedtuple('DomainInfo', 'domain, user, password')
adminuser = ''
adminpass = ''


@pytest.fixture(scope='session')
def session():
    return Session()


@pytest.fixture(scope='session')
def domain(session):
    from server_check import directadmin

    with Betamax(session).use_cassette('create_random_domain'):
        domain, user, password = directadmin.create_random_domain(adminuser, adminpass, session)
        return DomainInfo(domain, user, password)


def test_00_mysql_connection():
    from server_check import directadmin
    assert 'OK' in directadmin.test_mysql_connection()


def test_01_create_random_domain(domain):
    assert domain.user
    assert domain.password
    assert domain.user in domain.domain


def test_02_validPassword():
    from server_check import directadmin
    assert directadmin.validPassword('Aa12bcC') is True
    assert directadmin.validPassword('abc') is False


def test_03_enable_spamassassin(session, domain):
    from server_check import directadmin
    with Betamax(session).use_cassette('enable_spamassassin'):
        # Clear cookies to prevent sending empty "session" cookie.
        session.cookies.clear()
        assert directadmin.enable_spamassassin(domain.user, domain.password, domain.domain, session) is True


def test_04_remove_account(session, domain):
    from server_check import directadmin
    with Betamax(session).use_cassette('remove_account'):
        # Clear cookies to prevent sending empty "session" cookie.
        session.cookies.clear()
        assert directadmin.remove_account(adminuser, adminpass, domain.user, session) is True
