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

    def keep_running(self):
        return self._keep_running

    def signal_handler(self, signum, frame):
        if self.verbose and self._keep_running:
            print("You pressed ctrl-c")

        self._keep_running = False

class FileHandler():
    """Handle file and folder names."""

    root_folder = ""
    base_folder = ""
    prefix_char = "@"

    """Static methods. Utility."""
    @staticmethod
    def _add_folder(base, fdname):
        """Add a folder to a basename."""
        if fdname is None or fdname == "":
            return base
        if fdname.endswith("/"):
            fdname = fdname[:-1]
        return "{}{}/".format(base, fdname)

    @staticmethod
    def _add_name(base, name):
        """Add a name to a basename."""
        if name is None:
            return str(base) + "{}"
        return "{}{}".format(base, name)

    @staticmethod
    def _add_suffix(base, suffix):
        """Add a suffix to a basename."""
        if suffix is None or suffix == "":
            return base
        return "{}_{}".format(base, suffix)

    @staticmethod
    def _add_suffixes(base, *suffixes):
        """Add suffixes."""
        for s in suffixes:
            base = FileHandler._add_suffix(base, s)
        return base

    @staticmethod
    def _add_ext(base, ext):
        """Add a extension to a basename."""
        if ext is None or ext == "":
            return base
        if ext.startswith("."):
            ext = ext[1:] # Trim dot
        return "{}.{}".format(base, ext)

    @staticmethod
    def _add_config(base, prefix_char):
        """Add config prefix_char to a base fname."""
        return "{}{}".format(prefix_char, base)

    @staticmethod
    def trim_ext(name, ext):
        """Trim the extension of a name, if any."""
        full_ext = ".{}".format(ext)
        if name.endswith(full_ext):
            name = name[:-len(full_ext)]
        return name

    """Class methods. Use the root/base folders and other info."""
    @classmethod
    def _get_fname(cls, name, folder=None, suffix=None, ext=None, config=False):
        """Return the full filename, in the form: root/base/folders/name_suffix.ext."""

        # Add folder
        if type(folder) is list:
            fname = cls._get_folder(*folder)
        elif type(folder) is str:
            fname = cls._get_folder(folder)
        else:
            fname = cls._get_folder()

        # Add name
        fname = FileHandler._add_name(fname, name)

        # Add suffix (es)
        if type(suffix) is list:
            fname = FileHandler._add_suffixes(fname, *suffix)
        elif type(suffix) is str:
            fname = FileHandler._add_suffix(fname, suffix)

        # Add extension
        fname = FileHandler._add_ext(fname, ext)

        # Add config prefix_char (for parser)
        if config:
            fname = FileHandler._add_config(fname, cls.prefix_char)

        return fname

    @classmethod
    def _get_folder(cls, *folders):
        """Return the full folder, in the form: root/base/folders."""
        fname = FileHandler._add_folder("", cls.root_folder)
        fname = FileHandler._add_folder(fname, cls.base_folder)

        for fd in folders:
            fname = FileHandler._add_folder(fname, fd)

        return fname

    @classmethod
    def _assure_folder(cls, *folders):
        """Assure the existence of root/base/folder1/folder2/....

        If none folder is given, only the root/base is assured"""
        folder = cls._get_folder(*folders)
        if not os.path.exists(folder):
            os.makedirs(folder)
        # print("\t{}".format(folder)) # DEBUG
