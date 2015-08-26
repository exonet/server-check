from server_check import spamassassin
from server_check import exceptions
from mock import Mock
import poplib
import pytest


def test_00_test_spamassassin(domain):
    mockPOPlib = Mock(spec=poplib)
    mockPOP = Mock(spec=poplib.POP3('localhost'))

    # modify the conn.list and conn.retr calls
    popSpec = {
        'list.return_value': ['+OK 1 messages:', ['1 557'], 7],
        'retr.return_value': ['+OK:', ['X-Spam-Status: yes'], 0]
    }
    mockPOP.configure_mock(**popSpec)

    # Attach them
    # modify POP3() method to return mockPOP
    pop3LibSpec = {'POP3.return_value': mockPOP}
    mockPOPlib.configure_mock(**pop3LibSpec)

    assert "Test message contains SpamAssassin headers" in \
        spamassassin.test_spamassassin(domain.user, domain.domain, domain.password, mockPOPlib)


def test_01_test_spamassassin(domain):
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
        spamassassin.test_spamassassin(domain.user, domain.domain, domain.password, mockPOPlib)
    assert 'Retrieved message does not contain SpamAssassin headers' in err.value.message
