import pytest
from server_check import exceptions
from server_check import directadmin
from mock import patch, mock_open
import collections


def test_00_mysql_connection():
    mocked_open = mock_open(read_data='user=foo\npasswd=bar\n')
    with patch('MySQLdb.__init__'), \
            patch('MySQLdb.connect'), \
            patch('MySQLdb.cursors.DictCursor'), \
            patch('__builtin__.open', mocked_open):
        assert 'OK' in directadmin.test_mysql_connection()


def test_01_create_random_domain(domain):
    with patch('requests.post') as post, patch('__builtin__.open'), patch('subprocess.Popen'):
        domain, user, password = directadmin.create_random_domain("", "")
        assert domain
        assert password
        assert user in domain

        # Again but with false credentials.
        # Modify the session to return login page.
        postreturn = collections.namedtuple('post', 'text, status_code')
        postreturn.text = "DirectAdmin Login Page"
        post.return_value = postreturn
        with pytest.raises(exceptions.TestException) as err:
            domain, user, password = directadmin.create_random_domain("", "")
            assert 'DirectAdmin username or password incorrect' in err.value.message

        postreturn.text = 'error=1'
        post.return_value = postreturn

        with pytest.raises(exceptions.TestException) as err:
                domain, user, password = directadmin.create_random_domain("", "")
        assert 'Unable to create DirectAdmin user' in err.value.message


def test_02_validPassword():
    assert directadmin.validPassword('Aa12bcC')
    assert directadmin.validPassword('abc') is False


def test_03_enable_spamassassin(domain):
    with patch('requests.post') as post, patch('__builtin__.open'):
        assert directadmin.enable_spamassassin(domain.user, domain.password, domain.domain)

        # Again but with false credentials.
        postreturn = collections.namedtuple('post', 'text, status_code')
        postreturn.text = "DirectAdmin Login Page"
        post.return_value = postreturn
        with pytest.raises(exceptions.TestException) as err:
            directadmin.enable_spamassassin(domain.user, domain.password, domain.domain)
        assert 'DirectAdmin username or password incorrect' in err.value.message


def test_04_remove_account(domain):
    mocked_open = mock_open(read_data='user=foo\npasswd=bar\nSSL=1\nport=1234\n')
    with patch('requests.post') as post, patch('__builtin__.open', mocked_open):
        assert directadmin.remove_account("", "", domain.user)

        # Again but with false credentials.
        postreturn = collections.namedtuple('post', 'text, status_code')
        postreturn.text = "DirectAdmin Login Page"
        post.return_value = postreturn
        with pytest.raises(exceptions.TestException) as err:
            directadmin.remove_account("", "", domain.user)
        assert 'DirectAdmin username or password incorrect' in err.value.message

        # Again but with an account we already deleted.
        postreturn.text = "error=1"
        post.return_value = postreturn
        with pytest.raises(exceptions.TestException) as err:
            directadmin.remove_account("", "", domain.user)
        assert 'Unable to delete DirectAdmin user %s' % domain.user in err.value.message
