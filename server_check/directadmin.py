import os
import requests
import random
import string
import socket
import MySQLdb
import re
import subprocess
from exceptions import TestException

def get_api_url():
    scheme = "http"
    port = 2222
    with open('/usr/local/directadmin/conf/directadmin.conf', 'r') as fh:
        data = fh.read()
        for line in data.strip().split("\n"):
            key, value = line.strip().split('=')
            if key == 'SSL' and value == '1':
                scheme = 'https'
            if key == 'port':
                port = value

    return "%s://localhost:%s" % (scheme, port)

def test_mysql_connection():
    # Read MySQL username and password from /usr/local/directadmin/conf/mysql.conf.
    user = ""
    passwd = ""
    with open('/usr/local/directadmin/conf/mysql.conf', 'r') as fh:
        data = fh.read()
        for line in data.strip().split("\n"):
            key, value = line.strip().split('=')
            if key == 'user':
                user = value
            elif key == 'passwd':
                passwd = value

    # Try to create a connection.
    con = None
    con = MySQLdb.connect('localhost', user, passwd, 'mysql')
    cur = con.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT COUNT(User) AS usercount FROM user")
    if cur.rowcount:
        row = cur.fetchone()
        con.close()
        return "MySQL connection OK: %s users." % (row['usercount'])


def create_random_domain(adminuser, adminpass):
    user = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(6))
    domain = user + ".nl"

    password = ""
    while not validPassword(password):
        password = ''.join(random.SystemRandom().choice(
            string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(6))

    # Note, this might return 127.0.0.1.
    ip = socket.gethostbyname(socket.gethostname())

    account = {
        'action': 'create',
        'add': 'Submit',
        'domain': domain,
        'username': user,
        'passwd': password,
        'passwd2': password,
        'email': 'info@%s' % domain,
        'notify': 'no',
        'ubandwidth': 'ON',
        'uquota': 'ON',
        'uvdomains': 'ON',
        'unsubdomains': 'ON',
        'unemails': 'ON',
        'unemailf': 'ON',
        'unemailml': 'ON',
        'unemailr': 'ON',
        'umysql': 'ON',
        'udomainptr': 'ON',
        'uftp': 'ON',
        'aftp': 'ON',
        'cgi': 'ON',
        'php': 'ON',
        'spam': 'ON',
        'cron': 'ON',
        'catchall': 'ON',
        'ssl': 'ON',
        'ssh': 'ON',
        'sysinfo': 'ON',
        'dnscontrol': 'ON',
        'ip': ip
    }

    r = requests.post(
        '%s/CMD_API_ACCOUNT_USER' % get_api_url(),
        data=account,
        auth=(adminuser, adminpass),
        verify=False
    )

    if "DirectAdmin Login Page" in r.text:
        raise TestException("DirectAdmin username or password incorrect")
    elif "error=1" in r.text:
        raise TestException("Unable to create DirectAdmin user %s: %s" % (user, r.text))

    # In order to make sure we're connecting to the right virtualhost, we must add the domain to /etc/hosts.
    with open("/etc/hosts", "a") as fh:
        fh.write("%s\t\twww.%s\n" % (ip, domain))

    # Give httpd a reload to ensure the hostname is picked up.
    DEVNULL = open(os.devnull, 'wb')
    ret = subprocess.Popen(["/etc/init.d/httpd", "reload"], stdout=DEVNULL, stderr=DEVNULL)
    ret.wait()
    DEVNULL.close()

    return domain, user, password


def validPassword(password):
    uc = r'[A-Z]'
    lc = r'[a-z]'
    num = r'[0-9]'
    if re.search(uc, password) and re.search(lc, password) and re.search(num, password):
        return True

    return False


def remove_account(adminuser, adminpass, user):
    account = {
        'delete': 'yes',
        'confirmed': 'Confirm',
        'select0': user
    }

    r = requests.post(
        '%s/CMD_API_SELECT_USERS' % get_api_url(),
        data=account,
        auth=(adminuser, adminpass),
        verify=False
    )

    if "DirectAdmin Login Page" in r.text:
        raise TestException("DirectAdmin username or password incorrect")
    elif "error=1" in r.text:
        raise TestException("Unable to delete DirectAdmin user %s: %s" % (user, r.text))

    # Remove the entry from the hosts file.
    with open("/etc/hosts", "r+") as fh:
        content = fh.read()
        fh.seek(0)
        for line in content:
            if user + ".nl" not in line:
                fh.write(line)

    return True


def enable_spamassassin(user, passwd, domain):
    request = {
        'action': 'save',
        'domain': domain,
        'is_on': 'yes',
        'where': 'inbox',
        'required_hits': 5,
        'rewrite_subject': 0,
        'subject_tag': '',
        'report_safe': 1,
        'blacklist_from': '',
        'whitelist_from': '',
    }

    r = requests.post(
        '%s/CMD_API_SPAMASSASSIN' % get_api_url(),
        data=request,
        auth=(user, passwd),
        verify=False
    )

    if "DirectAdmin Login Page" in r.text:
        raise TestException("DirectAdmin username or password incorrect")

    return True
