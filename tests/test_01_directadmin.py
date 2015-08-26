import pytest
from server_check import exceptions
from server_check import directadmin
from mock import Mock
import requests
import collections


def test_00_mysql_connection():
    assert 'OK' in directadmin.test_mysql_connection()


def test_01_create_random_domain(domain, session):
    assert domain.user
    assert domain.password
    assert domain.user in domain.domain

    # modify the session to return login page
    postreturn = collections.namedtuple('post', 'text, status_code')
    postreturn.text = "DirectAdmin Login Page"
    sessionSpec = {'post.return_value': postreturn}
    session.configure_mock(**sessionSpec)

    # again but with false credentials
    with pytest.raises(exceptions.TestException) as err:
        domain, user, password = directadmin.create_random_domain("", "", session)
    assert 'DirectAdmin username or password incorrect' in err.value.message

    # again but mock the get return value to trigger error
    getreturn = collections.namedtuple('getreturn', 'text')
    getreturn.text = 'error=1'

    mockSession = Mock(spec=requests.Session)
    sessionSpec = {'post.return_value': getreturn}
    mockSession.configure_mock(**sessionSpec)

    # Again with modified return handler for session
    with pytest.raises(exceptions.TestException) as err:
            domain, user, password = directadmin.create_random_domain("", "", session=mockSession)
    assert 'Unable to create DirectAdmin user' in err.value.message

    # Reset session
    postreturn = collections.namedtuple('post', 'text, status_code')
    postreturn.text = "error=0"
    sessionSpec = {'post.return_value': postreturn}
    session.configure_mock(**sessionSpec)


def test_02_validPassword():
    assert directadmin.validPassword('Aa12bcC') is True
    assert directadmin.validPassword('abc') is False


def test_03_enable_spamassassin(session, domain):
    assert directadmin.enable_spamassassin(domain.user, domain.password, domain.domain, session) is True

    # again but with false credentials
    postreturn = collections.namedtuple('post', 'text, status_code')
    postreturn.text = "DirectAdmin Login Page"
    sessionSpec = {'post.return_value': postreturn}
    session.configure_mock(**sessionSpec)
    with pytest.raises(exceptions.TestException) as err:
        directadmin.enable_spamassassin(domain.user, domain.password, domain.domain, session)
    assert 'DirectAdmin username or password incorrect' in err.value.message

    # Reset session
    postreturn.text = "error=0"
    sessionSpec = {'post.return_value': postreturn}
    session.configure_mock(**sessionSpec)


def test_04_remove_account(session, domain):
    assert directadmin.remove_account("", "", domain.user, session) is True

    # again but with false credentials
    postreturn = collections.namedtuple('post', 'text, status_code')
    postreturn.text = "DirectAdmin Login Page"
    sessionSpec = {'post.return_value': postreturn}
    session.configure_mock(**sessionSpec)
    with pytest.raises(exceptions.TestException) as err:
        directadmin.remove_account("", "", domain.user, session)
    assert 'DirectAdmin username or password incorrect' in err.value.message

    # again but with an account we already deleted
    postreturn.text = "error=1"
    sessionSpec = {'post.return_value': postreturn}
    session.configure_mock(**sessionSpec)
    with pytest.raises(exceptions.TestException) as err:
        directadmin.remove_account("", "", domain.user, session)
    assert 'Unable to delete DirectAdmin user %s' % domain.user in err.value.message
