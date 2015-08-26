from server_check import ftp
from server_check import exceptions
from mock import Mock
import ftplib
import pytest


def test_00_test_ftp(domain):
    mockFtp = Mock(spec=ftplib)
    assert "Able to log in, upload, download and remove testfile via FTP." in \
        ftp.test_ftp(domain.user, domain.domain, domain.password, False, mockFtp)
    assert "Able to log in, upload, download and remove testfile via FTP_SSL." in \
        ftp.test_ftp(domain.user, domain.domain, domain.password, True, mockFtp)


def test_01_test_ftp(domain):
    mockFtplib = Mock(spec=ftplib)
    mockFtp = Mock(spec=ftplib.FTP())
    mockFtpTls = Mock(spec=ftplib.FTP_TLS())

    # modify login method so it throws ftplib.error_perm
    ftpSpec = {'login.side_effect': ftplib.error_perm}
    mockFtp.configure_mock(**ftpSpec)
    mockFtpTls.configure_mock(**ftpSpec)

    # Attach them
    # modify FTP() method to return mockFtp
    ftpLibSpec = {'FTP.return_value': mockFtp, 'FTP_TLS.return_value': mockFtpTls}
    mockFtplib.configure_mock(**ftpLibSpec)

    # then call it again
    with pytest.raises(exceptions.TestException) as err:
        ftp.test_ftp(domain.user, domain.domain, domain.password, False, mockFtplib)
    assert 'Permanent error while trying to log in.' in err.value.message


def test_02_download_handler():
    assert ftp.download_handler("this is a test") is True

    with pytest.raises(exceptions.TestException) as err:
        ftp.download_handler("this is not a test")
    assert 'Line not expected' in err.value.message
