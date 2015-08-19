import imaplib
from bcolors import error, ok, bcolors
import sys


def test_imap(user, domain, password, ssl=False):

    # Open an imap connection to localhost
    try:
        if not ssl:
            conn = imaplib.IMAP4('localhost')
        else:
            conn = imaplib.IMAP4_SSL('localhost')
    except StandardError, e:
        error("Unable to connect to IMAP: %s" % e)
        sys.exit(-1)

    # Login
    try:
        conn.login(user, password)

    except StandardError, e:
        error("Unable to login to IMAP: %s" % e)
        sys.exit(-1)

    # Fetch the last message (should be the only message, but hey)
    try:
        # Select the INBOX
        conn.select()

        # Search for messages
        typ, msgnums = conn.search(None, 'ALL')

        # Get the last messages
        msgids = msgnums[0].split()
        lastmsg = msgids[len(msgids) - 1]
        typ, data = conn.fetch(lastmsg, '(RFC822)')

        if 'da_server_check mail test' in data[0][1]:
            ok("Test message retrieved via Dovecot IMAP%s." % ("_SSL" if ssl else ""))
        else:
            error("Retrieved message does not contain test string:\n%s%s" % (bcolors.ENDC, data[0][1]))
            sys.exit(-1)

    except StandardError, e:
        error("Unable to list messages: %s" % e)
        sys.exit(-1)
