import imaplib
from exceptions import TestException


def test_imap(user, domain, password, ssl=False):
    # Open an imap connection to localhost.
    if not ssl:
        conn = imaplib.IMAP4('localhost')
    else:
        conn = imaplib.IMAP4_SSL('localhost')

    # Login.
    conn.login(user, password)

    # Fetch the last message (should be the only message, but hey).
    # Select the INBOX.
    conn.select()

    # Search for messages.
    typ, msgnums = conn.search(None, 'ALL')

    # Get the last messages.
    msgids = msgnums[0].split()
    lastmsg = msgids[len(msgids) - 1]
    typ, data = conn.fetch(lastmsg, '(RFC822)')

    if 'da_server_check mail test' in data[0][1]:
        return "Test message retrieved via Dovecot IMAP%s." % ("_SSL" if ssl else "")
    else:
        raise TestException("Retrieved message does not contain test string:\n%s" % (data[0][1]))
