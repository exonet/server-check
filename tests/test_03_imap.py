from server_check import imap
from server_check import exceptions
from mock import Mock
import imaplib
import pytest


def test_00_test_imap(domain):
    mockIMAPlib = Mock(spec=imaplib)
    mockIMAP = Mock(spec=imaplib.IMAP4)
    mockIMAP_SSL = Mock(spec=imaplib.IMAP4_SSL)

    # modify the conn.search and conn.fetch calls
    imapSpec = {
        'search.return_value': ['+OK', ['1 2 3']],
        'fetch.return_value': ['+OK:', [['', 'da_server_check mail test']]]
    }
    mockIMAP.configure_mock(**imapSpec)
    mockIMAP_SSL.configure_mock(**imapSpec)

    # Attach them
    # modify IMAP4() method to return mockIMAP
    imapLibSpec = {'IMAP4.return_value': mockIMAP, 'IMAP4_SSL.return_value': mockIMAP_SSL}
    mockIMAPlib.configure_mock(**imapLibSpec)

    assert "Test message retrieved via Dovecot IMAP." in \
        imap.test_imap(domain.user, domain.domain, domain.password, False, mockIMAPlib)
    assert "Test message retrieved via Dovecot IMAP_SSL." in \
        imap.test_imap(domain.user, domain.domain, domain.password, True, mockIMAPlib)


def test_01_test_imap(domain):
    mockIMAPlib = Mock(spec=imaplib)
    mockIMAP = Mock(spec=imaplib.IMAP4('localhost'))

    # modify the search and fetch calls
    imapSpec = {
        'search.return_value': ['+OK', ['1 2 3']],
        'fetch.return_value': ['+OK:', [['', 'unittest']]]
    }
    mockIMAP.configure_mock(**imapSpec)
    imapLibSpec = {'IMAP4.return_value': mockIMAP}
    mockIMAPlib.configure_mock(**imapLibSpec)

    with pytest.raises(exceptions.TestException) as err:
        imap.test_imap(domain.user, domain.domain, domain.password, False, mockIMAPlib)
    assert 'Retrieved message does not contain test string' in err.value.message
