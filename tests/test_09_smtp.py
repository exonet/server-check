from server_check import smtp
from mock import patch


@patch('smtplib.SMTP')
@patch('smtplib.SMTP_SSL')
def test_00_test_smtp(mockSMTP, domain):
    assert "Message successfully sent via SMTP on port 25." in \
        smtp.test_smtp(domain.user, domain.domain, domain.password, False, False)
    assert "Message successfully sent via SMTP on port 587." in \
        smtp.test_smtp(domain.user, domain.domain, domain.password, False, True)
    assert "Message successfully sent via SMTP_SSL on port 465." in \
        smtp.test_smtp(domain.user, domain.domain, domain.password, True, False)
    assert "Message successfully sent via SMTP with STARTTLS on port 25." in \
        smtp.test_smtp(domain.user, domain.domain, domain.password, False, False, True)
