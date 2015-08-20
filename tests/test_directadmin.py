from betamax import Betamax
from requests import Session
import pytest
import collections
from server_check import exceptions
from server_check import directadmin

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

    with Betamax(session).use_cassette('create_random_domain'):
        domain, user, password = directadmin.create_random_domain(adminuser, adminpass, session)
        return DomainInfo(domain, user, password)


def test_00_mysql_connection():
    assert 'OK' in directadmin.test_mysql_connection()


def test_01_create_random_domain(domain, session):
    assert domain.user
    assert domain.password
    assert domain.user in domain.domain

    # again but with known false information
    with pytest.raises(exceptions.TestException) as err:
        with Betamax(session).use_cassette('create_random_domain_false_info'):
            domain, user, password = directadmin.create_random_domain(adminuser, "foobar")
    assert 'DirectAdmin username or password incorrect' in err.value.message
    #with pytest.raises(exceptions.TestException) as err:
    #    with Betamax(session).use_cassette('create_random_domain_incorrect_info'):
    #        domain, user, password = directadmin.create_random_domain(
    #                adminuser, adminpass, session, "-invalidusername")
    #assert 'Unable to create DirectAdmin user' in err.value.message




def test_02_validPassword():
    assert directadmin.validPassword('Aa12bcC') is True
    assert directadmin.validPassword('abc') is False


def test_03_enable_spamassassin(session, domain):
    with Betamax(session).use_cassette('enable_spamassassin'):
        # Clear cookies to prevent sending empty "session" cookie.
        session.cookies.clear()
        assert directadmin.enable_spamassassin(domain.user, domain.password, domain.domain, session) is True


def test_04_remove_account(session, domain):
    with Betamax(session).use_cassette('remove_account'):
        # Clear cookies to prevent sending empty "session" cookie.
        session.cookies.clear()
        assert directadmin.remove_account(adminuser, adminpass, domain.user, session) is True
