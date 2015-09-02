import smtplib


def test_smtp(user, domain, password, ssl=False, submission=False):
    # See if we can connect to exim and send a message.
    port = 25 if not submission else 587
    if ssl:
        port = 465
    if not ssl:
        conn = smtplib.SMTP('localhost', port)
    else:
        conn = smtplib.SMTP_SSL('localhost')

    # Login to the server.
    conn.login(user, password)

    # Send a message.
    msg = "From: %s@%s\nTo: %s@%s\nSubject: exim test message\n\nfoo bar\n\
    X5O!P%%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*" % (user, domain, user, domain)
    conn.sendmail("%s@%s" % (user, domain), ["%s@%s" % (user, domain)], msg)

    # Disconnect.
    conn.quit()
    return "Message successfully sent via SMTP%s on port %s." % ("_SSL" if ssl else "", port)
