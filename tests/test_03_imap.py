import pytest
from mock import patch

from server_check import exceptions
from server_check import imap


def test_00_test_imap(domain):
    with patch('imaplib.IMAP4') as mock_imap:
        mock_imap.return_value.search.return_value = [b'+OK', [b'1 2 3']]
        mock_imap.return_value.fetch.return_value = [b'+OK:', [['', b'da_server_check mail test']]]

        assert "Test message retrieved via Dovecot IMAP." in \
            imap.test_imap(domain.user, domain.domain, domain.password)

    with patch('imaplib.IMAP4_SSL') as mock_imap_ssl:
        mock_imap_ssl.return_value.search.return_value = [b'+OK', [b'1 2 3']]
        mock_imap_ssl.return_value.fetch.return_value = [b'+OK:',
                                                         [[b'', b'da_server_check mail test']]]

        assert "Test message retrieved via Dovecot IMAP_SSL." in \
            imap.test_imap(domain.user, domain.domain, domain.password, True)


def test_01_test_imap(domain):
    with patch('imaplib.IMAP4') as mock_imap:
        mock_imap.return_value.search.return_value = [b'+OK', [b'1 2 3']]
        mock_imap.return_value.fetch.return_value = [b'+OK:', [[b'', b'unittest']]]

        with pytest.raises(exceptions.TestException) as err:
            imap.test_imap(domain.user, domain.domain, domain.password)
            assert 'Retrieved message does not contain test string' in err.value.message
