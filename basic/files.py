"""Submodule that provides a basic class t handle files."""
import os

class FileHandler():
    """Handle file and folder names."""

    root_folder = ""
    base_folder = ""
    prefix_char = "@"

    """Static methods. Utility."""
    @staticmethod
    def _add_suffix(base, suffix):
        """Add a suffix to a basename."""
        if suffix is None or suffix == "":
            return base
        return "_".join(base, suffix)

    @staticmethod
    def _add_suffixes(base, *suffixes):
        """Add suffixes."""
        for s in suffixes:
            base = FileHandler._add_suffix(base, s)
        return base

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
    def build_fname(cls, name, folder=None, suffix=None, ext=None, config=False):
        """Return the full filename, in the form: root/base/folders/name_suffix.ext."""

        if type(folder) is list:
            full_folder = cls.get_folder(*folder)
        elif type(folder) is str:
            full_folder = cls.get_folder(folder)
        else:
            full_folder = cls.get_folder()

        # Add name
        fname = os.path.join(full_folder, name)

        # Add suffix (es)
        if type(suffix) is list:
            fname = FileHandler._add_suffixes(fname, *suffix)
        elif type(suffix) is str:
            fname = FileHandler._add_suffix(fname, suffix)

        # Add extension
        fname = FileHandler._add_extension(fname, ext)
        if not ext is None and ext != "":
            if ext.startswith("."):
                fname = "".join(fname, ext)
            else:
                fname = ".".join(fname, ext)

        # Add config prefix_char (for parser)
        if config:
            fname = FileHandler._add_config(fname, cls.prefix_char)

        return fname

    @classmethod
    def _assure_folder(cls, *folders):
        """Assure the existence of root/base/folder1/folder2/....

        If none folder is given, only the root/base is assured"""
        folder = cls._get_folder(*folders)
        if not os.path.exists(folder):
            os.makedirs(folder)
        # print("\t{}".format(folder)) # DEBUG
