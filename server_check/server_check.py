#!/usr/bin/env python
try:
    import sys
    import os
    import argparse
    import directadmin
    import getpass
    import php
    import pop3
    import imap
    import smtp
    import ftp
    import spamassassin
    import phpmyadmin
    import roundcube
    import subprocess

    from bcolors import header, bcolors, ok, error, warning
except ImportError, e:
    print e
    print "\nERROR: one or more required python modules are missing."
    print "Run: pip install -r requirements.txt"
    sys.exit(1)


def parse_args(arguments=None):
    parser = argparse.ArgumentParser(
        description='Check a server to see if all components are still operating correctly.',
        epilog='If no options are specified, all checks will run.')
    parser.add_argument("-m", "--mysql", help='Run MySQL checks', dest='mysql', action='store_true')
    parser.add_argument("-P", "--php", help='Run PHP checks', dest='php', action='store_true')
    parser.add_argument("-p", "--pop3", help='Run POP3 checks', dest='pop3', action='store_true')
    parser.add_argument("-i", "--imap", help='Run IMAP checks', dest='imap', action='store_true')
    parser.add_argument("-f", "--ftp", help='Run FTP checks', dest='ftp', action='store_true')
    parser.add_argument("-S", "--smtp", help='Run SMTP checks', dest='smtp', action='store_true')
    parser.add_argument("-r", "--roundcube", help='Run RoundCube checks', dest='roundcube', action='store_true')
    parser.add_argument("-a", "--phpmyadmin", help='Run phpMyAdmin checks', dest='phpmyadmin', action='store_true')
    parser.add_argument("-s", "--spamassassin", help='Run SpamAssassin checks', dest='spamassassin',
                        action='store_true')

    args = parser.parse_args(arguments)

    # If none of the options are specified, enable them all.
    if (not args.mysql and not args.php and not args.pop3 and not args.imap and not args.ftp and
            not args.spamassassin and not args.smtp and not args.phpmyadmin and not args.roundcube):

        args.mysql = args.php = args.pop3 = args.imap = args.ftp = args.spamassassin = args.smtp = args.phpmyadmin\
            = args.roundcube = True

    return args


def main(argv=None):
    if os.geteuid() != 0:
        print warning("This script requires root privileges to run.")
        sys.exit(-1)

    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)

    domain = user = password = None

    try:
        # Detect DirectAdmin.
        if os.path.isfile("/usr/local/directadmin/conf/directadmin.conf"):
            print header("DirectAdmin")

            # Ask the user for a DirectAdmin login information.
            adminuser = raw_input(bcolors.BOLD + "DirectAdmin admin username: " + bcolors.ENDC)
            adminpass = getpass.getpass(bcolors.BOLD + "DirectAdmin admin password: " + bcolors.ENDC)

            # Create a new user in DirectAdmin.
            domain, user, password = directadmin.create_random_domain(adminuser, adminpass)

            # Instead of waiting for DirectAdmin's datasqk to do this, we do it manually.
            ret = subprocess.Popen(["/usr/bin/pure-pw", "mkdb", "/etc/pureftpd.pdb", "-f", "/etc/proftpd.passwd"])
            ret.wait()

            # Enable SpamAssassin.
            directadmin.enable_spamassassin(user, password, domain)

        else:
            print error("Only DirectAdmin servers are currently supported!")
            sys.exit(-1)

        if args.mysql:
            print header("MySQL")
            print ok(directadmin.test_mysql_connection())

        if args.php:
            print header("PHP")
            print ok(php.check_config())
            print ok(php.test_session_handler(user, domain))
            print ok(php.test_mod_ruid2(user, domain))
            print ok(php.test_mail(user, domain))

        if args.pop3:
            print header("POP3")
            print ok(pop3.test_pop3(user, domain, password))
            print ok(pop3.test_pop3(user, domain, password, ssl=True))

        if args.imap:
            print header("IMAP")
            print ok(imap.test_imap(user, domain, password))
            print ok(imap.test_imap(user, domain, password, ssl=True))

        if args.smtp:
            print header("SMTP")
            print ok(smtp.test_smtp(user, domain, password, ssl=False, submission=False))
            print ok(smtp.test_smtp(user, domain, password, ssl=False, submission=True))
            print ok(smtp.test_smtp(user, domain, password, ssl=True, submission=False))

        if args.ftp:
            print header("FTP")
            print ok(ftp.test_ftp(user, domain, password))
            print ok(ftp.test_ftp(user, domain, password, ssl=True))

        if args.spamassassin:
            print header("SpamAssassin")
            print ok(spamassassin.test_spamassassin(user, domain, password))

        if args.phpmyadmin:
            print header("phpMyAdmin")
            print ok(phpmyadmin.test_phpmyadmin())

        if args.roundcube:
            print header("Roundcube")
            print ok(roundcube.test_roundcube())

        # Finally, remove the account alltogether.
        directadmin.remove_account(adminuser, adminpass, user)
    except Exception as err:
        print error(err.message)

    return True
