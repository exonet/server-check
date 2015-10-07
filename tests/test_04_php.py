import pytest
from server_check import php
from server_check import exceptions
from mock import patch
import collections


def test_00_check_config(domain):
    with patch('subprocess.Popen') as popen:
        popen.return_value.communicate.return_value = ['config ok']

        assert "PHP config does not contain 'error' or 'warning'" in php.check_config()

        popen.return_value.communicate.return_value = ['error and warning']
        with pytest.raises(exceptions.TestException) as err:
            php.check_config()
        assert "Error or warning in output" in err.value.message


@patch('__builtin__.open')
@patch('os.chown')
def test_01_test_session_handler(mock_open, mock_chown, domain):
    with patch('requests.Session.get') as get:
        with patch('pwd.getpwnam') as pwnam:
            pwnam.return_value = ['', '', 0, 0]
            get_return = collections.namedtuple('get_return', 'text')
            get_return.text = 'test'
            get.return_value = get_return

            assert "Session handler OK." in php.test_session_handler(domain.user, domain.domain,
                                                                     checkstring='test')
            # Make it return something else for the session.
            get_return.text = 'foobar'
            get.return_value = get_return

            # Again with modified return handler for session.
            with pytest.raises(exceptions.TestException) as err:
                php.test_session_handler(domain.user, domain.domain)
            assert "Session handler not working" in err.value.message

        # Again with non-existing user.
        with pytest.raises(exceptions.TestException) as err:
            php.test_session_handler("foobar", domain.domain)
        assert "User foobar does not seem to exist on this system." in err.value.message


@patch('__builtin__.open')
@patch('os.chown')
def test_02_test_mod_ruid2(mock_open, mock_chown, domain):
    with patch('requests.get') as get:
        with patch('os.stat') as stat:
            with patch('pwd.getpwnam') as pwnam:
                pwnam.return_value = ['', '', 0, 0]
                get_return = collections.namedtuple('get_return', 'text, status_code')
                get_return.text = 'test'
                get_return.status_code = 200
                get.return_value = get_return

                stat_return = collections.namedtuple('stat', 'st_uid, st_gid')
                stat_return.st_uid = 0
                stat_return.st_gid = 0
                stat.return_value = stat_return

                assert "mod_ruid2 enabled and working." in php.test_mod_ruid2(domain.user, domain.domain)

                # Again with modified return handler for session.
                get_return.status_code = 500
                get.return_value = get_return
                with pytest.raises(exceptions.TestException) as err:
                    php.test_mod_ruid2(domain.user, domain.domain)
                assert "Unexpected response from getting" in err.value.message

                # Again with modified uids/gids.
                get_return.status_code = 200
                get.return_value = get_return
                stat_return.st_uid = 666
                stat_return.st_gid = 666
                stat.return_value = stat_return
                with pytest.raises(exceptions.TestException) as err:
                    php.test_mod_ruid2(domain.user, domain.domain)
                assert "has incorrect ownership" in err.value.message

            # Again with non-existing user.
            with pytest.raises(exceptions.TestException) as err:
                php.test_mod_ruid2("foobar", domain.domain)
            assert "User foobar does not seem to exist on this system." in err.value.message


@patch('__builtin__.open')
@patch('os.chown')
def test_03_test_mail(mock_open, mock_chown, domain):
    with patch('requests.get') as get:
        get_return = collections.namedtuple('get_return', 'text, status_code')
        get_return.text = 'OK'
        get_return.status_code = 200
        get.return_value = get_return

        with patch('pwd.getpwnam'):
            assert "mail sent succesfully" in php.test_mail(domain.user, domain.domain)

            get_return.status_code = 500
            get.return_value = get_return

            # Again with modified return handler for session.
            with pytest.raises(exceptions.TestException) as err:
                php.test_mail(domain.user, domain.domain)
            assert "Unexpected response from getting" in err.value.message

            # Again with proper statuscode but other text.
            get_return.status_code = 200
            get_return.text = 'test'
            with pytest.raises(exceptions.TestException) as err:
                php.test_mail(domain.user, domain.domain)
            assert "mail could not be sent" in err.value.message

        # Again with non-existing user.
        with pytest.raises(exceptions.TestException) as err:
            php.test_mail(domain.user, domain.domain)
        assert "User %s does not seem to exist on this system." % domain.user in err.value.message
