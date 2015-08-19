import poplib
from bcolors import error, ok
import sys


def test_pop3(user, domain, password, ssl=False):

    # Open a pop3 connection to localhost
    try:
        if not ssl:
            conn = poplib.POP3('localhost')
        else:
            conn = poplib.POP3_SSL('localhost')
    except StandardError, e:
        error("Unable to connect to POP3: %s" % e)
        sys.exit(-1)

    # Login
    try:
        conn.user(user)
        conn.pass_(password)

    except StandardError, e:
        error("Unable to login to POP3: %s" % e)
        sys.exit(-1)

    # Fetch the last message (should be the only message, but hey)
    try:
        # ('+OK 1 messages:', ['1 557'], 7)
        response, msglist, octets = conn.list()
        lastmsg = msglist[len(msglist) - 1]
        msgid, octets = lastmsg.split()

        # Get the message
        response, message, octets = conn.retr(msgid)
        found = False
        for line in message:
            if 'da_server_check mail test' in line:
                ok("Test message retrieved via Dovecot POP3%s." % ("_SSL" if ssl else ""))
                found = True
                break

        if not found:
            error("Retrieved message does not contain test string:\n%s" % '\n'.join(message))
            sys.exit(-1)

    except StandardError, e:
        error("Unable to list messages: %s" % e)
        sys.exit(-1)
