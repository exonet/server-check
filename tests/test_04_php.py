import pytest
from server_check import php
from server_check import exceptions
from mock import patch
import collections


def test_00_check_config(domain):
    with patch('subprocess.check_output') as check_output:
        check_output.return_value = 'config ok'

        assert "PHP config does not contain 'error' or 'warning'" in php.check_config()

        check_output.return_value = 'error and warning'
        with pytest.raises(exceptions.TestException) as err:
            php.check_config()
        assert "Error or warning in output" in err.value.message


def test_01_test_session_handler(domain):
    with patch('requests.Session.get') as get, patch('__builtin__.open'), patch('os.chown'):
        with patch('pwd.getpwnam') as pwnam:
            pwnam.return_value = ['', '', 0, 0]
            getreturn = collections.namedtuple('getreturn', 'text')
            getreturn.text = 'test'
            get.return_value = getreturn

            assert "Session handler OK." in php.test_session_handler(domain.user, domain.domain,
                                                                     checkstring='test')
            # Make it return something else for the session.
            getreturn.text = 'foobar'
            get.return_value = getreturn

            # Again with modified return handler for session.
            with pytest.raises(exceptions.TestException) as err:
                php.test_session_handler(domain.user, domain.domain)
            assert "Session handler not working" in err.value.message

        # Again with non-existing user.
        with pytest.raises(exceptions.TestException) as err:
            php.test_session_handler("foobar", domain.domain)
        assert "User foobar does not seem to exist on this system." in err.value.message


def test_02_test_mod_ruid2(domain):
    with patch('requests.get') as get, patch('__builtin__.open'), patch('os.chown'), patch('os.stat') as stat:
        with patch('pwd.getpwnam') as pwnam:
            pwnam.return_value = ['', '', 0, 0]
            getreturn = collections.namedtuple('getreturn', 'text, status_code')
            getreturn.text = 'test'
            getreturn.status_code = 200
            get.return_value = getreturn

            statreturn = collections.namedtuple('stat', 'st_uid, st_gid')
            statreturn.st_uid = 0
            statreturn.st_gid = 0
            stat.return_value = statreturn

            assert "mod_ruid2 enabled and working." in php.test_mod_ruid2(domain.user, domain.domain)

            # Again with modified return handler for session.
            getreturn.status_code = 500
            get.return_value = getreturn
            with pytest.raises(exceptions.TestException) as err:
                php.test_mod_ruid2(domain.user, domain.domain)
            assert "Unexpected response from getting" in err.value.message

            # Again with modified uids/gids.
            getreturn.status_code = 200
            get.return_value = getreturn
            statreturn.st_uid = 666
            statreturn.st_gid = 666
            stat.return_value = statreturn
            with pytest.raises(exceptions.TestException) as err:
                php.test_mod_ruid2(domain.user, domain.domain)
            assert "has incorrect ownership" in err.value.message

        # Again with non-existing user.
        with pytest.raises(exceptions.TestException) as err:
            php.test_mod_ruid2("foobar", domain.domain)
        assert "User foobar does not seem to exist on this system." in err.value.message


def test_03_test_mail(domain):
    with patch('__builtin__.open'), patch('os.chown'), patch('requests.get') as get:
        getreturn = collections.namedtuple('getreturn', 'text, status_code')
        getreturn.text = 'OK'
        getreturn.status_code = 200
        get.return_value = getreturn

        with patch('pwd.getpwnam'):
            assert "mail sent succesfully" in php.test_mail(domain.user, domain.domain)

            getreturn.status_code = 500
            get.return_value = getreturn

            # Again with modified return handler for session.
            with pytest.raises(exceptions.TestException) as err:
                php.test_mail(domain.user, domain.domain)
            assert "Unexpected response from getting" in err.value.message

            # Again with proper statuscode but other text.
            getreturn.status_code = 200
            getreturn.text = 'test'
            with pytest.raises(exceptions.TestException) as err:
                php.test_mail(domain.user, domain.domain)
            assert "mail could not be sent" in err.value.message

        # Again with non-existing user.
        with pytest.raises(exceptions.TestException) as err:
            php.test_mail(domain.user, domain.domain)
        assert "User %s does not seem to exist on this system." % domain.user in err.value.message
