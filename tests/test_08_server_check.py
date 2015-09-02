import pytest
import sys
from mock import patch


def test_00_import():
    # Empty sys.path so import is guaranteed to fail.
    path = sys.path
    sys.path = ['.']

    with pytest.raises(SystemExit):
        from server_check import server_check
        server_check.parse_args([])

    # Restore PATH.
    sys.path = path


def test_01_parse_args():
    from server_check import server_check
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


def test_02_main():
    from server_check import server_check
    with patch('__builtin__.raw_input') as rawinput, \
            patch('getpass.getpass') as getpass, \
            patch('subprocess.Popen'), \
            patch('os.geteuid') as geteuid, \
            patch('os.path.isfile') as isfile:

        rawinput.return_value = "foo"
        getpass.return_value = "bar"

        geteuid.return_value = 0

        assert server_check.main([])

        # Fake not-finding directadmin.conf.
        isfile.return_value = False
        with pytest.raises(SystemExit):
            server_check.main([])
        isfile.return_value = True

        # Check without arguments.
        argv = sys.argv
        sys.argv = ['']
        assert server_check.main()
        sys.argv = argv

        # Without root.
        geteuid.return_value = 1000
        with pytest.raises(SystemExit):
            server_check.main([])


@patch('server_check.server_check.directadmin')
@patch('server_check.server_check.php')
@patch('server_check.server_check.pop3')
@patch('server_check.server_check.imap')
@patch('server_check.server_check.smtp')
@patch('server_check.server_check.ftp')
@patch('server_check.server_check.spamassassin')
@patch('server_check.server_check.roundcube')
@patch('server_check.server_check.phpmyadmin')
def test_03_main(phpmyadmin, roundcube, spamassassin, ftp, smtp, imap, pop3, php, directadmin):
    from server_check import server_check
    with patch('__builtin__.raw_input') as rawinput, \
            patch('getpass.getpass') as getpass, \
            patch('subprocess.Popen'), \
            patch('os.geteuid') as geteuid, \
            patch('os.path.isfile') as isfile:

        isfile.return_value = True
        rawinput.return_value = "foo"
        getpass.return_value = "bar"

        geteuid.return_value = 0
        directadmin.create_random_domain.return_value = ['foo', 'bar', 'baz']

        assert server_check.main([])
