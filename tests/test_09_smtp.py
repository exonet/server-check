from server_check import smtp
from mock import patch


def test_00_test_smtp(domain):
    with patch('smtplib.SMTP'), patch('smtplib.SMTP_SSL'):
        assert "Message successfully sent via SMTP on port 25." in \
            smtp.test_smtp(domain.user, domain.domain, domain.password, False, False)
        assert "Message successfully sent via SMTP on port 587." in \
            smtp.test_smtp(domain.user, domain.domain, domain.password, False, True)
        assert "Message successfully sent via SMTP_SSL on port 465." in \
            smtp.test_smtp(domain.user, domain.domain, domain.password, True, False)
