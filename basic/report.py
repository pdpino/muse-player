"""Submodule that provides functions to report to console."""


def report(text, *args, end="\n", level=1):
    """Display a message in the console"""
    try:
        text = text.format(*args)
    except IndexError:
        # the amount of args don't match the amount of brackets
        pass
    msg = "{}{}".format("\t" * level, text)
    print(msg, flush=True, end=end)
    
class ProgressReporter:
    """Wrapper to report the progress of a process."""


    def __init__(self, msje=None):
        """Constructor. If a message is provided, report it."""
        self._report(msje)


    def _report(self, msje):
        """Report a message."""
        if not msje is None:
            report(msje)

    def start(self, n_total, msje=None, n_reports=20):
        """Set the config for reporting a process."""
        self.n = n_total
        self.m = n_total // n_reports
        self.i = 0 # counter

        self._report(msje)

    def next(self):
        """Report the progress of a process."""
        self.i += 1
        if self.i % self.m == 0:
            print("\r", end="", flush=True) # Borrar anterior
            # print("\t\t{} de {}".format(i, n), end="", flush=True)
            print("\t\t{:.2f} %".format(self.i/self.n*100), end="", flush=True) # display percentage

    def end(self, msje=None):
        """Report the end of a process."""
        print("\n", end="", flush=True)
        self._report(msje)
