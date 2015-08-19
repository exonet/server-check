from bcolors import ok, error
import smtplib


def test_smtp(user, domain, password, ssl=False, submission=False):

    # See if we can connect to exim and send a message
    try:
        port = 25 if not submission else 587
        if ssl:
            port = 465
        if not ssl:
            conn = smtplib.SMTP('localhost', port)
        else:
            conn = smtplib.SMTP_SSL('localhost')

    except smtplib.SMTPException, e:
        error("Unable to connect to SMTP%s on port %s: %s" % ("_SSL" if ssl else "", port, e))

    # Login to the server
    try:
        conn.login(user, password)
    except smtplib.SMTPException, e:
        error("Unable to authenticate: %s" % (e))
        return

    # Send a message
    try:
        msg = "From: %s@%s\nTo: %s@%s\nSubject: exim test message\n\nfoo bar\n\
        X5O!P%%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*" % (user, domain, user, domain)
        conn.sendmail("%s@%s" % (user, domain), ["%s@%s" % (user, domain)], msg)

    except smtplib.SMTPException, e:
        error("Unable to send message: %s" % (e))
        return

    # Disconnect
    try:
        conn.quit()
        ok("Message successfully sent via SMTP%s on port %s." % ("_SSL" if ssl else "", port))
    except smtplib.SMTPException, e:
        error("Unable to disconnect: %s" % (e))
