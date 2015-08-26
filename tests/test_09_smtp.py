from server_check import smtp
from mock import Mock
import smtplib


def test_00_test_smtp(domain):
    mockSMTPlib = Mock(spec=smtplib)

    assert "Message successfully sent via SMTP on port 25." in \
        smtp.test_smtp(domain.user, domain.domain, domain.password, False, False, mockSMTPlib)
    assert "Message successfully sent via SMTP on port 587." in \
        smtp.test_smtp(domain.user, domain.domain, domain.password, False, True, mockSMTPlib)
    assert "Message successfully sent via SMTP_SSL on port 465." in \
        smtp.test_smtp(domain.user, domain.domain, domain.password, True, False, mockSMTPlib)
