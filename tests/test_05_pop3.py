from server_check import pop3
from server_check import exceptions
from mock import patch
import pytest


def test_00_test_pop3(domain):
    with patch('poplib.POP3') as mockpop:
        mockpop.return_value.list.return_value = [b'+OK 1 messages:', [b'1 557'], 7]
        mockpop.return_value.retr.return_value = [b'+OK:', [b'', b'da_server_check mail test'], 0]

        assert "Test message retrieved via Dovecot POP3." in \
            pop3.test_pop3(domain.user, domain.domain, domain.password)

    with patch('poplib.POP3_SSL') as mockpopssl:
        mockpopssl.return_value.list.return_value = [b'+OK 1 messages:', [b'1 557'], 7]
        mockpopssl.return_value.retr.return_value = [b'+OK:', [b'', b'da_server_check mail test'], 0]

        assert "Test message retrieved via Dovecot POP3_SSL." in \
            pop3.test_pop3(domain.user, domain.domain, domain.password, True)


def test_01_test_pop3(domain):
    with patch('poplib.POP3') as mockpop:
        mockpop.return_value.list.return_value = [b'+OK 1 messages:', [b'1 557'], 7]
        mockpop.return_value.retr.return_value = [b'+OK:', [b'', b'unittest'], 0]

        with pytest.raises(exceptions.TestException) as err:
            pop3.test_pop3(domain.user, domain.domain, domain.password, delay=None)
            assert 'Retrieved message does not contain test string' in err.value.message
