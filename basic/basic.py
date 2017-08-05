"""Provide a set of basic functions"""
import sys
import signal

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

def sec2hr(t):
    """Transform the seconds in H:M
    Adapted from: http://stackoverflow.com/a/33504562"""

    m, s = divmod(t, 60) # obtener minutos, segundos
    h, m = divmod(m, 60) # obtener horas, minutos
    d, h = divmod(h, 24) # obtener dias, horas

    # patterns:
    patt_sec = "{:.1f}s"
    patt_min = "{:.0f}m "
    patt_hr = "{:.0f}h "
    patt_d = "{:.0f} days, "

    if d == 0:
        if h == 0:
            if m == 0:
                return patt_sec.format(s)
            else:
                pattern = patt_min + patt_sec
                return pattern.format(m, s)
        else:
            pattern = patt_hr + patt_min + patt_sec
            return pattern.format(h, m, s)
    else:
        pattern = patt_d + patt_hr + patt_min + patt_sec
        return pattern.format(d, h, m, s)

class SignalCatcher(object):
    """Catch a ctrl-c signal """
    def __init__(self, verbose=True):
        self._keep_running = True
        self.verbose = verbose

        signal.signal(signal.SIGINT, self.signal_handler)

    def keep_running(self):
        return self._keep_running

    def signal_handler(self, signum, frame):
        if self.verbose and self._keep_running:
            print("You pressed ctrl-c")

        self._keep_running = False
