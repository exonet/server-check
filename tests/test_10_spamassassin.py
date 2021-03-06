from server_check import spamassassin
from server_check import exceptions
from mock import patch
import pytest


def test_00_test_spamassassin(domain):
    with patch('poplib.POP3') as mockpop:
        mockpop.return_value.list.return_value = [b'+OK 1 messages:', [b'1 557'], 7]
        mockpop.return_value.retr.return_value = [b'+OK:', [b'', b'X-Spam-Status: yes'], 0]

        assert "Test message contains SpamAssassin headers" in \
            spamassassin.test_spamassassin(domain.user, domain.domain, domain.password)


def test_01_test_spamassassin(domain):
    with patch('poplib.POP3') as mockpop:
        mockpop.return_value.list.return_value = [b'+OK 1 messages:', [b'1 557'], 7]
        mockpop.return_value.retr.return_value = [b'+OK:', [b'', b'unittest'], 0]

        with pytest.raises(exceptions.TestException) as err:
            spamassassin.test_spamassassin(domain.user, domain.domain, domain.password, delay=None)
            assert 'Retrieved message does not contain SpamAssassin headers' in err.value.message
