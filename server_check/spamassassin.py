import poplib
from bcolors import error, ok, warning
import sys
import time


def test_spamassassin(user, domain, password):
    time.sleep(10)

    # Open a pop3 connection to localhost
    try:
        conn = poplib.POP3('localhost')
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
        found = False
        for msg in msglist:
            msgid, octets = msg.split()

            # Get the message
            response, message, octets = conn.retr(msgid)
            for line in message:
                if 'X-Spam-Status' in line:
                    ok("Test message contains SpamAssassin headers (message %s)." % msgid)
                    found = True
                    break

            if not found:
                warning("SpamAssassin headers not (yet) found, message %s" % msgid)

        if not found:
            error("Retrieved message does not contain SpamAssassin headers:\n%s" % '\n'.join(message))
            sys.exit(-1)

    except StandardError, e:
        error("Unable to list messages: %s" % e)
        sys.exit(-1)
