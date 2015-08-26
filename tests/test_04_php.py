import pytest
from server_check import php
from server_check import exceptions
from mock import Mock
import os
import subprocess
import requests
import collections


def test_00_check_config(domain):
    sub = Mock(spec=subprocess)

    # set subprocess.check_output return value
    subSpec = {'check_output.return_value': 'config ok'}
    sub.configure_mock(**subSpec)

    assert "PHP config does not contain 'error' or 'warning'" in php.check_config(sub)

    # Again but now with error
    subSpec = {'check_output.return_value': 'error and warning'}
    sub.configure_mock(**subSpec)

    with pytest.raises(exceptions.TestException) as err:
        php.check_config(sub)
    assert "Error or warning in output" in err.value.message


def test_01_test_session_handler(domain, session, mockpwd):
    getreturn = collections.namedtuple('getreturn', 'text')
    getreturn.text = 'test'
    sessionSpec = {'get.return_value': getreturn}
    session.configure_mock(**sessionSpec)

    assert "Session handler OK." in php.test_session_handler(domain.user, domain.domain,
                                                             checkstring='test', session=session, pwd=mockpwd)

    # Again with non-existing user
    with pytest.raises(exceptions.TestException) as err:
        php.test_session_handler("foobar", domain.domain, session=session)
    assert "User foobar does not seem to exist on this system." in err.value.message

    # Now mock the requests object, make it return something else for the session
    getreturn = collections.namedtuple('getreturn', 'text')
    getreturn.text = 'foobar'

    sessionSpec = {'get.return_value': getreturn}
    session.configure_mock(**sessionSpec)

    # Again with modified return handler for session
    with pytest.raises(exceptions.TestException) as err:
        php.test_session_handler(domain.user, domain.domain, session=session, pwd=mockpwd)
    assert "Session handler not working" in err.value.message


def test_02_test_mod_ruid2(domain, session, mockpwd):
    getreturn = collections.namedtuple('getreturn', 'text, status_code')
    getreturn.text = 'test'
    getreturn.status_code = 200
    sessionSpec = {'get.return_value': getreturn}
    session.configure_mock(**sessionSpec)

    statreturn = collections.namedtuple('stat', 'st_uid, st_gid')
    statreturn.st_uid = 0
    statreturn.st_gid = 0

    # Mock os lib
    mockOs = Mock(spec=os)
    osSpec = {'stat.return_value': statreturn}
    mockOs.configure_mock(**osSpec)

    assert "mod_ruid2 enabled and working." in php.test_mod_ruid2(domain.user, domain.domain,
                                                                  session=session, pwd=mockpwd, os=mockOs)

    # Again with non-existing user
    with pytest.raises(exceptions.TestException) as err:
        php.test_mod_ruid2("foobar", domain.domain, session=session)
    assert "User foobar does not seem to exist on this system." in err.value.message

    # Now mock the requests object, make it return something else for the session
    getreturn = collections.namedtuple('getreturn', 'text, status_code')
    getreturn.text = 'foobar'
    getreturn.status_code = 500

    mockSession = Mock(spec=requests.Session)
    sessionSpec = {'get.return_value': getreturn}
    mockSession.configure_mock(**sessionSpec)

    # Again with modified return handler for session
    with pytest.raises(exceptions.TestException) as err:
        php.test_mod_ruid2(domain.user, domain.domain, session=mockSession, pwd=mockpwd)
    assert "Unexpected response from getting" in err.value.message

    # Fake wrong ownership
    statreturn.st_uid = 666
    statreturn.st_gid = 666

    # Mock os lib
    mockOs = Mock(spec=os)
    osSpec = {'stat.return_value': statreturn}
    mockOs.configure_mock(**osSpec)

    # Again with modified uids/gids
    with pytest.raises(exceptions.TestException) as err:
        php.test_mod_ruid2(domain.user, domain.domain, session=session, pwd=mockpwd, os=mockOs)
    assert "has incorrect ownership" in err.value.message


def test_03_test_mail(domain, session, mockpwd):
    getreturn = collections.namedtuple('getreturn', 'text, status_code')
    getreturn.text = 'OK'
    getreturn.status_code = 200
    sessionSpec = {'get.return_value': getreturn}
    session.configure_mock(**sessionSpec)

    assert "mail sent succesfully" in php.test_mail(domain.user, domain.domain, session=session, pwd=mockpwd)

    # Again with non-existing user
    with pytest.raises(exceptions.TestException) as err:
        php.test_mail(domain.user, domain.domain, session=session)
    assert "User %s does not seem to exist on this system." % domain.user in err.value.message

    # Mock status code
    getreturn.status_code = 500

    mockSession = Mock(spec=requests.Session)
    sessionSpec = {'get.return_value': getreturn}
    mockSession.configure_mock(**sessionSpec)

    # Again with modified return handler for session
    with pytest.raises(exceptions.TestException) as err:
        php.test_mail(domain.user, domain.domain, session=mockSession, pwd=mockpwd)
    assert "Unexpected response from getting" in err.value.message

    # Again with proper statuscode but other text
    getreturn.status_code = 200
    getreturn.text = 'test'
    with pytest.raises(exceptions.TestException) as err:
        php.test_mail(domain.user, domain.domain, session=mockSession, pwd=mockpwd)
    assert "mail could not be sent" in err.value.message
