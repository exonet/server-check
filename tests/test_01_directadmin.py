import collections

import pytest
from mock import patch, mock_open

from server_check import directadmin
from server_check import exceptions


@patch('mysql.connector.connect')
def test_00_mysql_connection(mock_connect):
    mocked_open = mock_open(read_data='user=foo\npasswd=bar\n')
    with patch('server_check.directadmin.open', mocked_open):
        directadmin.test_mysql_connection()
        assert mock_connect.called_with(host='localhost', user='foo', password='bar',
                                        database='mysql')


@patch('server_check.directadmin.open')
@patch('subprocess.Popen')
def test_01_create_random_domain(mock_popen, mock_open, domain):
    with patch('requests.post') as post:
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


def test_02_valid_password():
    assert directadmin.valid_password('Aa12bcC')
    assert directadmin.valid_password('abc') is False


@patch('server_check.directadmin.open')
def test_03_enable_spamassassin(mock_open, domain):
    with patch('requests.post') as post:
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
    with patch('server_check.directadmin.open', mocked_open):
        with patch('requests.post') as post:
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
