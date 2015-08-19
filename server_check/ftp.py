from bcolors import ok, error
import ftplib
import time
import subprocess


def test_ftp(user, domain, password, restart=False, ssl=False):

    # Instead of waiting for DirectAdmin's datasqk to do this, we do it manually
    # pure-pw mkdb /etc/pureftpd.pdb -f /etc/proftpd.passwd
    ret = subprocess.Popen(["/usr/bin/pure-pw", "mkdb", "/etc/pureftpd.pdb", "-f", "/etc/proftpd.passwd"])
    ret.wait()

    # See if we can connect to FTP and upload, download and remove a file
    try:
        if not ssl:
            conn = ftplib.FTP('localhost')
        else:
            conn = ftplib.FTP_TLS('localhost')

    except ftplib.error_perm, e:
        error("Permanent error: %s" % (e))
        return
    except ftplib.error_temp, e:
        error("Temporary error: %s" % (e))
        return
    except ftplib.error_proto, e:
        error("Protocol error: %s" % (e))
        return
    except ftplib.error_reply, e:
        error("Unexpected reply error: %s" % (e))
        return

    # Login to the server
    tries = 0
    err = None
    while tries < 3:
        try:
            conn.login(user, password)
            break
        except ftplib.error_perm, e:
            # Sleep for a second, it's possible the server is still creating the FTP account
            tries += 1
            time.sleep(1)
            err = e
        except ftplib.error_temp, e:
            tries += 1
            time.sleep(1)
            err = e
        except ftplib.error_proto, e:
            error("Protocol error: %s" % (e))
            return
        except ftplib.error_reply, e:
            error("Unexpected reply error: %s" % (e))
            return

    if tries >= 3:
        error("Permanent error: %s" % (err))
        return

    # switch to secure data connection
    if ssl:
        try:
            conn.prot_p()
        except ftplib.error_perm, e:
            error("Permanent error: %s" % (e))
            return
        except ftplib.error_temp, e:
            error("Temporary error: %s" % (e))
            return
        except ftplib.error_proto, e:
            error("Protocol error: %s" % (e))
            return
        except ftplib.error_reply, e:
            error("Unexpected reply error: %s" % (e))
            return

    # Upload a file
    try:
        with open("ftp_test.txt", "w") as fh:
            fh.write("this is a test")

        with open("ftp_test.txt", "r") as fh:
            conn.storlines("STOR ftp_test.txt", fh)

        ok("Upload of ftp_test.txt succesful.")
    except ftplib.error_perm, e:
        error("Permanent error: %s" % (e))
        return
    except ftplib.error_temp, e:
        error("Temporary error: %s" % (e))
        return
    except ftplib.error_proto, e:
        error("Protocol error: %s" % (e))
        return
    except ftplib.error_reply, e:
        error("Unexpected reply error: %s" % (e))
        return

    # Download a file
    try:
        conn.retrlines("RETR ftp_test.txt", download_handler)

        ok("Download of ftp_test.txt succesful.")
    except ftplib.error_perm, e:
        error("Permanent error: %s" % (e))
        return
    except ftplib.error_temp, e:
        error("Temporary error: %s" % (e))
        return
    except ftplib.error_proto, e:
        error("Protocol error: %s" % (e))
        return
    except ftplib.error_reply, e:
        error("Unexpected reply error: %s" % (e))
        return

    # Delete a file
    try:
        conn.delete("ftp_test.txt")

        ok("Delete of ftp_test.txt succesful.")
    except ftplib.error_perm, e:
        error("Permanent error: %s" % (e))
        return
    except ftplib.error_temp, e:
        error("Temporary error: %s" % (e))
        return
    except ftplib.error_proto, e:
        error("Protocol error: %s" % (e))
        return
    except ftplib.error_reply, e:
        error("Unexpected reply error: %s" % (e))
        return

    # Disconnect
    try:
        conn.quit()
    except ftplib.error_perm, e:
        error("Permanent error: %s" % (e))
        return
    except ftplib.error_temp, e:
        error("Temporary error: %s" % (e))
        return
    except ftplib.error_proto, e:
        error("Protocol error: %s" % (e))
        return
    except ftplib.error_reply, e:
        error("Unexpected reply error: %s" % (e))
        return


def download_handler(line):
    if "this is a test" in line:
        ok("Downloaded file contains test string.")
    else:
        error("Line not expected: %s" % line)
