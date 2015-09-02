import poplib
from exceptions import TestException
import time


def test_spamassassin(user, domain, password):
    # We need to wait a few seconds to ensure the message has been delivered.
    time.sleep(3)

    # Open a pop3 connection to localhost.
    conn = poplib.POP3('localhost')

    # Login.
    conn.user(user)
    conn.pass_(password)

    # Fetch the last message (should be the only message, but hey).
    response, msglist, octets = conn.list()
    for msg in msglist:
        msgid, octets = msg.split()

        # Get the message.
        response, message, octets = conn.retr(msgid)
        for line in message:
            if 'X-Spam-Status' in line:
                return "Test message contains SpamAssassin headers (message %s)." % msgid

    raise TestException("Retrieved message does not contain SpamAssassin headers:\n%s" % '\n'.join(message))
