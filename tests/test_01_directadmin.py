import pytest
from server_check import exceptions
from server_check import directadmin
from mock import Mock, MagicMock, patch
import mock
import requests
import collections
import MySQLdb
from MySQLdb.cursors import DictCursor, BaseCursor
from MySQLdb.connections import Connection


def test_00_mysql_connection():

    mocked_open = mock.mock_open(read_data='user=foo\npasswd=bar\n')
    with patch('MySQLdb.__init__'), patch('MySQLdb.connect'), patch('server_check.directadmin.open', mocked_open):
        assert 'OK' in directadmin.test_mysql_connection()


def test_01_create_random_domain(domain):
    with patch('requests.post') as post, patch('server_check.directadmin.open'), patch('subprocess.Popen'):
        domain, user, password = directadmin.create_random_domain("", "")
        assert domain
        assert password
        assert user in domain

        # again but with false credentials
        # modify the session to return login page
        postreturn = collections.namedtuple('post', 'text, status_code')
        postreturn.text = "DirectAdmin Login Page"
        post.return_value=postreturn
        with pytest.raises(exceptions.TestException) as err:
            domain, user, password = directadmin.create_random_domain("", "")
            assert 'DirectAdmin username or password incorrect' in err.value.message

        postreturn.text = 'error=1'
        post.return_value=postreturn

        with pytest.raises(exceptions.TestException) as err:
                domain, user, password = directadmin.create_random_domain("", "")
        assert 'Unable to create DirectAdmin user' in err.value.message


def test_02_validPassword():
    assert directadmin.validPassword('Aa12bcC') is True
    assert directadmin.validPassword('abc') is False


def test_03_enable_spamassassin(domain):
    with patch('requests.post') as post:
        assert directadmin.enable_spamassassin(domain.user, domain.password, domain.domain) is True

        # again but with false credentials
        postreturn = collections.namedtuple('post', 'text, status_code')
        postreturn.text = "DirectAdmin Login Page"
        post.return_value=postreturn
        with pytest.raises(exceptions.TestException) as err:
            directadmin.enable_spamassassin(domain.user, domain.password, domain.domain)
        assert 'DirectAdmin username or password incorrect' in err.value.message


def test_04_remove_account(domain):
    mocked_open = mock.mock_open(read_data='user=foo\npasswd=bar\n')
    with patch('requests.post') as post, patch('server_check.directadmin.open', mocked_open):
        assert directadmin.remove_account("", "", domain.user) is True

        # again but with false credentials
        postreturn = collections.namedtuple('post', 'text, status_code')
        postreturn.text = "DirectAdmin Login Page"
        post.return_value=postreturn
        with pytest.raises(exceptions.TestException) as err:
            directadmin.remove_account("", "", domain.user)
        assert 'DirectAdmin username or password incorrect' in err.value.message

        # again but with an account we already deleted
        postreturn.text = "error=1"
        post.return_value=postreturn
        with pytest.raises(exceptions.TestException) as err:
            directadmin.remove_account("", "", domain.user)
        assert 'Unable to delete DirectAdmin user %s' % domain.user in err.value.message
