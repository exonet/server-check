class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def error(msg):
    return "[%s ERROR %s] %s%s%s" % (
        Bcolors.FAIL, Bcolors.ENDC, Bcolors.BOLD, msg, Bcolors.ENDC)


def warning(msg):
    return "[%sWARNING%s] %s%s%s" % (
        Bcolors.WARNING, Bcolors.ENDC, Bcolors.BOLD, msg, Bcolors.ENDC)


def ok(msg):
    return "[%s  OK   %s] %s" % (
        Bcolors.OKGREEN, Bcolors.ENDC, msg)


def header(msg):
    numdash = 40 - len(msg)

    return "\n=== %s%sChecking %s%s %s" % (
        Bcolors.BOLD, Bcolors.HEADER, msg, Bcolors.ENDC, "=" * numdash)
