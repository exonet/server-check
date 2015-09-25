import poplib
import time
from exceptions import TestException


def test_pop3(user, domain, password, ssl=False):
    # Sleep a while to allow the previous test to deliver the message in the mailbox.
    time.sleep(3)

    # Open a pop3 connection to localhost.
    if not ssl:
        conn = poplib.POP3('localhost')
    else:
        conn = poplib.POP3_SSL('localhost')

    # Login.
    conn.user(user)
    conn.pass_(password)

    # Fetch the last message (should be the only message, but hey).
    response, msglist, octets = conn.list()
    lastmsg = msglist[len(msglist) - 1]
    msgid, octets = lastmsg.split()

    # Get the message.
    response, message, octets = conn.retr(msgid)
    for line in message:
        if 'da_server_check mail test' in line:
            return "Test message retrieved via Dovecot POP3%s." % ("_SSL" if ssl else "")

    raise TestException("Retrieved message does not contain test string:\n%s" % '\n'.join(message))
