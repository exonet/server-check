import poplib
import time

from .exceptions import TestException


def test_spamassassin(user, domain, password, delay=1):
    # Fetch all messages and see if it contains SpamAssassin headers
    attempt = 1
    message = []
    while attempt <= 10:
        # Open a pop3 connection to localhost.
        conn = poplib.POP3('localhost')

        # Login.
        conn.user(user)
        conn.pass_(password)

        response, msglist, octets = conn.list()
        for msg in msglist:
            msgid, octets = msg.split()

            # Get the message.
            response, message, octets = conn.retr(msgid.decode())
            for line in message:
                if 'X-Spam-Status' in line.decode():
                    return "Test message contains SpamAssassin headers (message %s)." \
                           % msgid.decode()

        attempt += 1
        conn.quit()
        if delay:
            time.sleep(delay)

    raise TestException(
        "Retrieved message does not contain SpamAssassin headers:\n{}".format(b'\n'.join(message)))
