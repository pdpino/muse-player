"""Submodule that provides signal handling."""
import signal

def mute_ctrlc():
    """Inhabilitates ctrl-c."""
    def nothing(signum, frame):
        pass
    signal.signal(signal.SIGINT, nothing)

class SignalCatcher(object):
    """Catch a ctrl-c signal """
    def __init__(self, verbose=True):
        """Constructor."""
        self._keep_running = True
        self.verbose = verbose

        signal.signal(signal.SIGINT, self.signal_handler)

    def keep_running(self):
        """Return the inner bool."""
        return self._keep_running

    def signal_handler(self, signum, frame):
        """Handles the ctrl-c."""
        if self.verbose and self._keep_running:
            print("You pressed ctrl-c")

        self._keep_running = False
