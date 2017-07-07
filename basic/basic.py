"""Provide a set of basic functions"""
import sys

def perror(text, exit_code=1, force_continue=False, **kwargs):
    """Prints to standard error. If status is non-zero exits."""

    # See how bad is it
    bad = "WARN" if force_continue else "ERROR"

    print("{}: {}".format(bad, text), file=sys.stderr, **kwargs)
    if exit_code != 0 and not force_continue:
        sys.exit(exit_code)


def assure_startswith(word, prefix):
    """Assure that a string starts with a given prefix"""
    if not word.startswith(prefix):
        word = prefix + word
    return word


class SignalCatcher(object):
    """Catch a ctrl-c signal """
    def __init__(self, verbose=True):
        self._keep_running = True
        self.verbose = verbose

    def keep_running(self):
        return self._keep_running

    def signal_handler(self, signum, frame):
        if self.verbose and self._keep_running:
            print("You pressed ctrl-c")

        self._keep_running = False
