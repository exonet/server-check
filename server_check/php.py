import subprocess
import requests
import random
import string
import pwd
import os
import time
from exceptions import TestException


def check_config():
    output = subprocess.check_output(["php", "-v"], stderr=subprocess.STDOUT)

    if 'error' in output.lower() or 'warning' in output.lower():
        raise TestException("Error or warning in output:\n%s" % output)

    return "PHP config does not contain 'error' or 'warning'"


def test_session_handler(user, domain, checkstring=None):
    # Sleep a second to ensure the httpd has restarted.
    time.sleep(3)

    if checkstring is None:
        checkstring = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(6))

    try:
        userent = pwd.getpwnam(user)
    except:
        raise TestException("User %s does not seem to exist on this system." % user)

    uid = userent[2]
    gid = userent[3]

    # Write two php files that will demonstrate the working of the session handler.
    with open("/home/%s/domains/%s/public_html/session_test_1.php" % (user, domain), 'w') as fh:
        fh.write("<?php\nsession_start();\n$_SESSION['identifier'] = '%s';\n?>\n" % checkstring)
    os.chown("/home/%s/domains/%s/public_html/session_test_1.php" % (user, domain), uid, gid)

    with open("/home/%s/domains/%s/public_html/session_test_2.php" % (user, domain), 'w') as fh:
        fh.write("<?php\nsession_start();\necho $_SESSION['identifier'];\n?>\n")
    os.chown("/home/%s/domains/%s/public_html/session_test_2.php" % (user, domain), uid, gid)

    # Now, call the first file and store the session id.
    # We want to make sure we call this via the webserver instead of the cli.
    # Initialize the session on the server.
    s = requests.Session()
    s.get('http://www.%s/session_test_1.php' % domain)
    # Request the second page, this should return the checkstring.
    r = s.get('http://www.%s/session_test_2.php' % domain)

    if r.text == checkstring:
        return "Session handler OK."
    else:
        raise TestException("Session handler not working: %s != %s" % (r.text, checkstring))


def test_mod_ruid2(user, domain):
    try:
        userent = pwd.getpwnam(user)
    except:
        raise TestException("User %s does not seem to exist on this system." % user)

    uid = userent[2]
    gid = userent[3]

    # Write a PHP file that writes a txt file so we can check ownership.
    with open("/home/%s/domains/%s/public_html/mod_ruid2_test.php" % (user, domain), 'w') as fh:
        fh.write("<?php\n file_put_contents('/home/%s/domains/%s/public_html/mod_ruid2.txt','foo');\n?>\n"
                 % (user, domain))
    os.chown("/home/%s/domains/%s/public_html/mod_ruid2_test.php" % (user, domain), uid, gid)

    # Make sure, before we start, the file does not exist.
    try:
        os.remove("/home/%s/domains/%s/public_html/mod_ruid2.txt" % (user, domain))
    except:
        # We ignore raise TestExceptions because the file probably didn't exist to begin with.
        pass

    # Access the php file so the file is created.
    r = requests.get('http://www.%s/mod_ruid2_test.php' % domain)

    if r.status_code != 200:
        raise TestException("Unexpected response from getting http://www.%s/mod_ruid2_test.php: %s %s"
                            % (domain, r.status_code, r.text))
    else:
        # See if the file was created and ownership is right.
        fuid = os.stat("/home/%s/domains/%s/public_html/mod_ruid2.txt" % (user, domain)).st_uid
        fgid = os.stat("/home/%s/domains/%s/public_html/mod_ruid2.txt" % (user, domain)).st_gid
        if fuid == uid and fgid == gid:
            return "mod_ruid2 enabled and working."
        else:
            raise TestException("file /home/%s/domains/%s/public_html/mod_ruid2.txt has incorrect ownership: uid is %s\
                    (expected: %s), gid is %s (expected: %s)" % (user, domain, fuid, uid, fgid, gid))


def test_mail(user, domain):
    try:
        userent = pwd.getpwnam(user)
    except:
        raise TestException("User %s does not seem to exist on this system." % user)

    uid = userent[2]
    gid = userent[3]

    # Write a PHP file that sends an e-mail to user@domain.
    with open("/home/%s/domains/%s/public_html/mail_test.php" % (user, domain), 'w') as fh:
        fh.write("<?php\n if (mail('%s@%s','da_server_check mail test','da_server_check mail test'))\n\techo 'OK';\
\nelse\n\techo 'FAILED';\n?>\n"
                 % (user, domain))
    os.chown("/home/%s/domains/%s/public_html/mail_test.php" % (user, domain), uid, gid)

    # Access the php file so the mail is sent.
    r = requests.get('http://www.%s/mail_test.php' % domain)

    if r.status_code != 200:
        raise TestException("Unexpected response from getting http://www.%s/mod_ruid2_test.php: %s %s"
                            % (domain, r.status_code, r.text))
    else:
        # See if OK was in the response.
        if 'OK' in r.text:
            # Sleep a second to ensure the mail has been delivered.
            time.sleep(1)

            return "mail sent succesfully"
        else:
            raise TestException("mail could not be sent (output = '%s'!)" % r.text)
