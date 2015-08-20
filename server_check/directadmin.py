# apt-get install python-requests
import requests
import random
import string
import socket
import MySQLdb
import re
# import time
from exceptions import TestException


def test_mysql_connection():
    # Read MySQL username and password from /usr/local/directadmin/conf/mysql.conf
    user = ""
    passwd = ""
    with open('/usr/local/directadmin/conf/mysql.conf', 'r') as fh:
        for line in fh:
            # user=xxx
            # passwd=xxxx
            key, value = line.strip().split('=')
            if key == 'user':
                user = value
            elif key == 'passwd':
                passwd = value

    # Try to create a connection
    con = None
    con = MySQLdb.connect('localhost', user, passwd, 'mysql')
    cur = con.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT COUNT(User) AS usercount FROM user")
    if cur.rowcount:
        row = cur.fetchone()
        con.close()
        return "MySQL connection OK: %s users." % (row['usercount'])


def create_random_domain(adminuser, adminpass, session=requests.Session(), user=None):
    if user is None:
        user = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(6))

    domain = user + ".nl"
    password = ""
    while not validPassword(password):
        password = ''.join(random.SystemRandom().choice(
            string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(6))

    ip = socket.gethostbyname(socket.gethostname())  # Note, this might return 127.0.0.1

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

    r = session.post(
        'http://localhost:2222/CMD_API_ACCOUNT_USER',
        data=account,
        auth=(adminuser, adminpass)
    )

    if "DirectAdmin Login Page" in r.text:
        raise TestException("DirectAdmin username or password incorrect")
    elif "error=1" in r.text:
        raise TestException("Unable to create DirectAdmin user %s: %s" % (user, r.text))

    return domain, user, password


def validPassword(password):
    uc = r'[A-Z]'
    lc = r'[a-z]'
    num = r'[0-9]'
    if re.search(uc, password) and re.search(lc, password) and re.search(num, password):
        return True

    return False


def remove_account(adminuser, adminpass, user, session=requests.Session()):
    account = {
        'delete': 'yes',
        'confirmed': 'Confirm',
        'select0': user
    }

    r = session.post(
        'http://localhost:2222/CMD_API_SELECT_USERS',
        data=account,
        auth=(adminuser, adminpass)
    )

    if "DirectAdmin Login Page" in r.text:
        raise TestException("DirectAdmin username or password incorrect")
    elif "error=1" in r.text:
        raise TestException("Unable to delete DirectAdmin user %s: %s" % (user, r.text))

    return True


def enable_spamassassin(user, passwd, domain, session=requests.Session()):

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

    r = session.post(
        'http://localhost:2222/CMD_API_SPAMASSASSIN',
        data=request,
        auth=(user, passwd)
    )

    if "DirectAdmin Login Page" in r.text:
        raise TestException("DirectAdmin username or password incorrect")
    elif "error=1" in r.text:
        raise TestException("Unable to enable SpamAssassin for %s: %s" % (domain, r.text))

    return True
