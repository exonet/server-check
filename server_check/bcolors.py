class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def error(msg):
    return "[%s ERROR %s] %s%s%s" % (bcolors.FAIL, bcolors.ENDC, bcolors.BOLD, msg, bcolors.ENDC)


def warning(msg):
    return "[%sWARNING%s] %s%s%s" % (bcolors.WARNING, bcolors.ENDC, bcolors.BOLD, msg, bcolors.ENDC)


def ok(msg):
    return "[%s  OK   %s] %s" % (bcolors.OKGREEN, bcolors.ENDC, msg)


def header(msg):
    numdash = 40 - len(msg)

    return "\n=== %s%sChecking %s%s %s" % (bcolors.BOLD, bcolors.HEADER, msg, bcolors.ENDC, "=" * numdash)
