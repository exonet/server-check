import pytest
import sys
from mock import patch, mock_open


def test_00_parse_args():
    import server_check
    arguments = ['-m']

    args = server_check.parse_args(arguments)
    # Ensure only args.mysql is True.
    assert args.mysql
    assert args.php is False
    assert args.pop3 is False
    assert args.imap is False
    assert args.ftp is False
    assert args.smtp is False
    assert args.roundcube is False
    assert args.phpmyadmin is False
    assert args.spamassassin is False

    arguments = []
    args = server_check.parse_args(arguments)
    # Ensure everything is True.
    assert args.mysql
    assert args.php
    assert args.pop3
    assert args.imap
    assert args.ftp
    assert args.smtp
    assert args.roundcube
    assert args.phpmyadmin
    assert args.spamassassin


@patch('subprocess.Popen')
def test_01_main(mockpopen):
    import server_check
    with patch('__builtin__.raw_input') as mock_raw_input:
        with patch('getpass.getpass') as mock_getpass:
            with patch('os.geteuid') as mock_geteuid:
                with patch('os.path.isfile') as mock_isfile:

                    mock_isfile.return_value = True
                    mock_raw_input.return_value = "foo"
                    mock_getpass.return_value = "bar"
                    mock_geteuid.return_value = 0

                    assert server_check.main([])

                    # Fake not-finding directadmin.conf.
                    mock_isfile.return_value = False
                    with pytest.raises(SystemExit):
                        server_check.main([])
                    mock_isfile.return_value = True

                    # Check without arguments.
                    argv = sys.argv
                    sys.argv = ['']
                    assert server_check.main()
                    sys.argv = argv

                    # Without root.
                    mock_geteuid.return_value = 1000
                    with pytest.raises(SystemExit):
                        server_check.main([])


@patch('subprocess.Popen')
@patch('server_check.directadmin')
@patch('server_check.php')
@patch('server_check.pop3')
@patch('server_check.imap')
@patch('server_check.smtp')
@patch('server_check.ftp')
@patch('server_check.spamassassin')
@patch('server_check.roundcube')
@patch('server_check.phpmyadmin')
def test_02_main(phpmyadmin, roundcube, spamassassin, ftp, smtp, imap, pop3, php, directadmin,
                 mockpopen):
    import server_check
    with patch('__builtin__.raw_input') as mock_raw_input:
        with patch('getpass.getpass') as mock_getpass:
            with patch('os.geteuid') as mock_geteuid:
                with patch('os.path.isfile') as mock_isfile:

                    mock_isfile.return_value = True
                    mock_raw_input.return_value = "foo"
                    mock_getpass.return_value = "bar"

                    mock_geteuid.return_value = 0
                    directadmin.create_random_domain.return_value = ['foo', 'bar', 'baz']

                    mocked_open = mock_open(read_data='465\n')
                    with patch('__builtin__.open', mocked_open):
                        assert server_check.main([])
