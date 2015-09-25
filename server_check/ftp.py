import ftplib
import time
from exceptions import TestException


def test_ftp(user, domain, password, ssl=False):
    # See if we can connect to FTP and upload, download and remove a file.
    if not ssl:
        conn = ftplib.FTP('localhost')
    else:
        conn = ftplib.FTP_TLS('localhost')

    # Login to the server.
    tries = 0
    while tries < 3:
        try:
            conn.login(user, password)
            break
        except Exception:
            tries += 1
            time.sleep(1)

    if tries >= 3:
        raise TestException("Permanent error while trying to log in.")

    # Switch to secure data connection.
    if ssl:
        conn.prot_p()

    # Upload a file.
    with open("ftp_test.txt", "w") as fh:
        fh.write("this is a test")

    with open("ftp_test.txt", "r") as fh:
        conn.storlines("STOR ftp_test.txt", fh)

    # Download a file.
    conn.retrlines("RETR ftp_test.txt", download_handler)

    # Delete a file.
    conn.delete("ftp_test.txt")

    # Disconnect.
    conn.quit()

    return "Able to log in, upload, download and remove testfile via FTP%s." % ("_SSL" if ssl else "")


def download_handler(line):
    if "this is a test" in line:
        return True
    else:
        raise TestException("Line not expected: %s" % line)
