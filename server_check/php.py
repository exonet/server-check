import subprocess
import requests
import random
import string
import socket
import pwd
import os
import time
from exceptions import TestException


def check_config():
    output = subprocess.check_output(["php", "-v"], stderr=subprocess.STDOUT)

    if 'error' in output.lower() or 'warning' in output.lower():
        raise TestException("Error or warning in output:\n%s" % output)

    return "PHP config does not contain 'error' or 'warning'"


def test_session_handler(user, domain):
    checkstring = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(6))
    userent = pwd.getpwnam(user)

    if userent is None:
        raise TestException("User %s does not seem to exist on this system." % user)

    uid = userent[2]
    gid = userent[3]

    # Write two php files that will demonstrate the working of the session handler
    with open("/home/%s/domains/%s/public_html/session_test_1.php" % (user, domain), 'w') as fh:
        fh.write("<?\nsession_start();\n$_SESSION['identifier'] = '%s';\n?>\n" % checkstring)
    os.chown("/home/%s/domains/%s/public_html/session_test_1.php" % (user, domain), uid, gid)

    with open("/home/%s/domains/%s/public_html/session_test_2.php" % (user, domain), 'w') as fh:
        fh.write("<?\nsession_start();\necho $_SESSION['identifier'];\n?>\n")
    os.chown("/home/%s/domains/%s/public_html/session_test_2.php" % (user, domain), uid, gid)

    # Now, call the first file and store the session id
    # We want to make sure we call this via the webserver instead of the cli
    # In order to make sure we're connecting to the right virtualhost, we must add the domain to /etc/hosts
    ip = socket.gethostbyname(socket.gethostname())  # Note, this might return 127.0.0.1

    with open("/etc/hosts", "a") as fh:
        fh.write("%s\t\twww.%s\n" % (ip, domain))

    # Give httpd a reload to ensure the hostname is picked up
    DEVNULL = open(os.devnull, 'wb')
    ret = subprocess.Popen(["/etc/init.d/httpd", "reload"], stdout=DEVNULL, stderr=DEVNULL)
    ret.wait()
    DEVNULL.close()

    s = requests.Session()
    # Initialize the session on the server
    s.get('http://www.%s/session_test_1.php' % domain)
    # Request the second page, this should return the checkstring
    r = s.get('http://www.%s/session_test_2.php' % domain)
    if r.text == checkstring:
        return "Session handler OK."
    else:
        raise TestException("Session handler not working: %s != %s" % (r.text, checkstring))

    # remove the entry from the hosts file
    with open("/etc/hosts", "r+") as fh:
        content = fh.read()
        fh.seek(0)
        for line in content:
            if domain not in line:
                fh.write(line)


def test_mod_ruid2(user, domain):
    userent = pwd.getpwnam(user)

    if userent is None:
        raise TestException("User %s does not seem to exist on this system." % user)

    uid = userent[2]
    gid = userent[3]

    # Write a PHP file that writes a txt file so we can check ownership
    with open("/home/%s/domains/%s/public_html/mod_ruid2_test.php" % (user, domain), 'w') as fh:
        fh.write("<?\n file_put_contents('/home/%s/domains/%s/public_html/mod_ruid2.txt','foo');\n?>\n"
                 % (user, domain))
    os.chown("/home/%s/domains/%s/public_html/mod_ruid2_test.php" % (user, domain), uid, gid)

    # We want to make sure we call this via the webserver instead of the cli
    # In order to make sure we're connecting to the right virtualhost, we must add the domain to /etc/hosts
    ip = socket.gethostbyname(socket.gethostname())  # Note, this might return 127.0.0.1

    with open("/etc/hosts", "a") as fh:
        fh.write("%s\t\twww.%s\n" % (ip, domain))

    # Make sure, before we start, the file does not exist
    try:
        os.remove("/home/%s/domains/%s/public_html/mod_ruid2.txt" % (user, domain))
    except:
        pass  # We ignore raise TestExceptions because the file probably didn't exist to begin with

    # Access the php file so the file is created
    r = requests.get('http://www.%s/mod_ruid2_test.php' % domain)
    if r.status_code != 200:
        raise TestException("Unexpected response from getting http://www.%s/mod_ruid2_test.php: %s %s"
                            % (domain, r.status_code, r.text))
    else:
        # See if the file was created and ownership is right
        fuid = os.stat("/home/%s/domains/%s/public_html/mod_ruid2.txt" % (user, domain)).st_uid
        fgid = os.stat("/home/%s/domains/%s/public_html/mod_ruid2.txt" % (user, domain)).st_gid
        if fuid == uid and fgid == gid:
            return "mod_ruid2 enabled and working."
        else:
            raise TestException("file /home/%s/domains/%s/public_html/mod_ruid2.txt has incorrect ownership: uid is %s\
                    (expected: %s), gid is %s (expected: %s)" % (user, domain, fuid, uid, fgid, gid))

    # remove the entry from the hosts file
    with open("/etc/hosts", "r+") as fh:
        content = fh.read()
        fh.seek(0)
        for line in content:
            if domain not in line:
                fh.write(line)


def test_mail(user, domain):
    userent = pwd.getpwnam(user)

    if userent is None:
        raise TestException("User %s does not seem to exist on this system." % user)

    uid = userent[2]
    gid = userent[3]

    # Write a PHP file that sends an e-mail to user@domain
    with open("/home/%s/domains/%s/public_html/mail_test.php" % (user, domain), 'w') as fh:
        fh.write("<?\n if (mail('%s@%s','da_server_check mail test','da_server_check mail test'))\n\techo 'OK';\
\nelse\n\techo 'FAILED';\n?>\n"
                 % (user, domain))
    os.chown("/home/%s/domains/%s/public_html/mail_test.php" % (user, domain), uid, gid)

    # We want to make sure we call this via the webserver instead of the cli
    # In order to make sure we're connecting to the right virtualhost, we must add the domain to /etc/hosts
    ip = socket.gethostbyname(socket.gethostname())  # Note, this might return 127.0.0.1

    with open("/etc/hosts", "a") as fh:
        fh.write("%s\t\twww.%s\n" % (ip, domain))

    # Access the php file so the mail is sent
    r = requests.get('http://www.%s/mail_test.php' % domain)
    if r.status_code != 200:
        raise TestException("Unexpected response from getting http://www.%s/mod_ruid2_test.php: %s %s"
                            % (domain, r.status_code, r.text))
    else:
        # See if OK was in the response
        if 'OK' in r.text:
            return "mail sent succesfully"

            # Sleep a second to ensure the mail has been delivered
            time.sleep(1)
        else:
            raise TestException("mail could not be sent (output = '%s'!)" % r.text)

    # remove the entry from the hosts file
    with open("/etc/hosts", "r+") as fh:
        content = fh.read()
        fh.seek(0)
        for line in content:
            if domain not in line:
                fh.write(line)
