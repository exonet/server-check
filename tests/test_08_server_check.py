import pytest
import sys
import os
import getpass
import subprocess
from mock import Mock


def test_00_import():
    # Empty sys.path so import is guaranteed to fail
    path = sys.path
    sys.path = []
    # Empty modules
    toremove = []
    for mod in sys.modules:
        if 'server_check.' in mod or 'test_' in mod:
            toremove.append(mod)
    for mod in toremove:
        del sys.modules[mod]
    if 'poplib' in sys.modules:
        del sys.modules['poplib']

    with pytest.raises(SystemExit):
        from server_check import server_check
        server_check.parse_args([])

    # Restore PATH
    sys.path = path


def test_01_parse_args():
    from server_check import server_check
    arguments = ['-m']

    args = server_check.parse_args(arguments)
    # Ensure only args.mysql is True
    assert args.mysql is True
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
    # Ensure everything is True
    assert args.mysql is True
    assert args.php is True
    assert args.pop3 is True
    assert args.imap is True
    assert args.ftp is True
    assert args.smtp is True
    assert args.roundcube is True
    assert args.phpmyadmin is True
    assert args.spamassassin is True


def test_02_main():
    from server_check import server_check
    from server_check import directadmin
    from server_check import php
    from server_check import pop3
    from server_check import imap
    from server_check import smtp
    from server_check import ftp
    from server_check import spamassassin
    from server_check import phpmyadmin
    from server_check import roundcube
    assert server_check.main([]) is True

    # Check on uid
    mockOs = Mock(spec=os)
    osSpec = {'geteuid.return_value': 1000}
    mockOs.configure_mock(**osSpec)
    with pytest.raises(SystemExit):
        server_check.main([], os=mockOs)

    # Fake not-finding directadmin.conf
    mock_os_path = Mock(spec=os.path)
    pathSpec = {'isfile.return_value': False}
    mock_os_path.configure_mock(**pathSpec)
    osSpec = {'geteuid.return_value': 0}
    mockOs.attach_mock(mock_os_path, 'path')
    mockOs.configure_mock(**osSpec)
    with pytest.raises(SystemExit):
        server_check.main([], os=mockOs)

    # Check without arguments
    with pytest.raises(SystemExit):
        server_check.main()

    # Modify raw_input, getpass, subprocess to return bogus info
    mock_raw_input = Mock(spec=raw_input)
    mock_getpass = Mock(spec=getpass)
    getpassSpec = {'getpass.return_value': 'foo'}
    mock_getpass.configure_mock(**getpassSpec)
    mock_subprocess = Mock(spec=subprocess)
    mock_da = Mock(spec=directadmin)
    daSpec = {'create_random_domain.return_value': ['foo', 'bar', 'baz']}
    mock_da.configure_mock(**daSpec)

    mockphp = Mock(spec=php)
    mockpop3 = Mock(spec=pop3)
    mockimap = Mock(spec=imap)
    mocksmtp = Mock(spec=smtp)
    mockftp = Mock(spec=ftp)
    mockspamassassin = Mock(spec=spamassassin)
    mockphpmyadmin = Mock(spec=phpmyadmin)
    mockroundcube = Mock(spec=roundcube)

    assert server_check.main(
        [],
        os=os,
        raw_input=mock_raw_input,
        getpass=mock_getpass,
        subprocess=mock_subprocess,
        directadmin=mock_da,
        php=mockphp,
        pop3=mockpop3,
        imap=mockimap,
        smtp=mocksmtp,
        ftp=mockftp,
        spamassassin=mockspamassassin,
        phpmyadmin=mockphpmyadmin,
        roundcube=mockroundcube
        ) is True
