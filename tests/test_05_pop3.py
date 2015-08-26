from server_check import pop3
from server_check import exceptions
from mock import Mock
import poplib
import pytest


def test_00_test_pop3(domain):
    mockPOPlib = Mock(spec=poplib)
    mockPOP = Mock(spec=poplib.POP3('localhost'))
    mockPOP_SSL = Mock(spec=poplib.POP3_SSL('localhost'))

    # modify the conn.list and conn.retr calls
    popSpec = {
        'list.return_value': ['+OK 1 messages:', ['1 557'], 7],
        'retr.return_value': ['+OK:', ['da_server_check mail test'], 0]
    }
    mockPOP.configure_mock(**popSpec)
    mockPOP_SSL.configure_mock(**popSpec)

    # Attach them
    # modify POP3() method to return mockPOP
    pop3LibSpec = {'POP3.return_value': mockPOP, 'POP3_SSL.return_value': mockPOP_SSL}
    mockPOPlib.configure_mock(**pop3LibSpec)

    assert "Test message retrieved via Dovecot POP3." in \
        pop3.test_pop3(domain.user, domain.domain, domain.password, False, mockPOPlib)
    assert "Test message retrieved via Dovecot POP3_SSL." in \
        pop3.test_pop3(domain.user, domain.domain, domain.password, True, mockPOPlib)


def test_01_test_pop3(domain):
    mockPOPlib = Mock(spec=poplib)
    mockPOP = Mock(spec=poplib.POP3('localhost'))

    # modify the conn.list and conn.retr calls
    popSpec = {
        'list.return_value': ['+OK 1 messages:', ['1 557'], 7],
        'retr.return_value': ['+OK:', ['unittest'], 0]
    }
    mockPOP.configure_mock(**popSpec)
    pop3LibSpec = {'POP3.return_value': mockPOP}
    mockPOPlib.configure_mock(**pop3LibSpec)

    with pytest.raises(exceptions.TestException) as err:
        pop3.test_pop3(domain.user, domain.domain, domain.password, False, mockPOPlib)
    assert 'Retrieved message does not contain test string' in err.value.message
