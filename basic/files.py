"""Submodule that provides a basic class t handle files."""
import os

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
