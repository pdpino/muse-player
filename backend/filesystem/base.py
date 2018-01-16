"""Module that provides functionality to manage the data"""
import os
import shutil
from backend import basic

def _smart_concat(base, something, separator):
    """Concatenates base separator and something smartly (without repeating the separator)."""
    if something is None or something == "":
        return base
    if something.startswith(separator):
        something = something[1:]
    if base.endswith(separator):
        base = base[:-1]
    return separator.join([base, something])

class BaseFileHandler():
    """Base static class to handle load and save of files.

    The base directory is:
        root/base/main/
    Usually you will use:
        - root: ./
        - base: a folder to separate with the rest of your files
        - main: will be overriden by the specific classes that inherit from this one

    Tipically, only the methods save_data() and load_data() will be overriden.
    """

    name = "base" # just a tag
    root_folder = ""
    base_folder = "data"
    main_folder = "main"
    suffix_separator = "_"
    extension = "csv"

    @classmethod
    def add_suffix(cls, base, suffix):
        if type(suffix) is list:
            for suffix in suffixes:
                base = _smart_concat(base, suffix, cls.suffix_separator)
            return base
        else:
            return _smart_concat(base, suffix, cls.suffix_separator)

    @classmethod
    def assure_folder(cls, *folders, debug=False):
        """Assure the existence of root/base/main/folders/...

        If none folder is given, only the root/base is assured"""
        folder = cls.get_folder(*folders)
        if not os.path.exists(folder):
            if debug:
                print("Assure {}-files would create: {}".format(cls.name, folder))
            else:
                os.makedirs(folder)
                print("Assure {}-files created: {}".format(cls.name, folder))

    @classmethod
    def get_folder(cls, *folders):
        """Return the full folder, in the form: root/base/main/folders."""
        return os.path.join(cls.root_folder, cls.base_folder, cls.main_folder, *folders)

    @classmethod
    def get_fname(cls, name, folder=None, suffix=None, extension=None, **kwargs):
        """Return the full filename, in the form: root/base/folders/name_suffix.ext

        folder -- subfolder(s) to add to the main folder
        suffix -- string or list of suffixes
        extension -- if provided, overrides the class extension
        kwargs -- ignored kwargs
        """

        if type(folder) is list:
            full_folder = cls.get_folder(*folder)
        elif type(folder) is str:
            full_folder = cls.get_folder(folder)
        else:
            full_folder = cls.get_folder()

        fname = os.path.join(full_folder, name)
        fname = cls.add_suffix(fname, suffix)
        fname = _smart_concat(fname, extension or cls.extension, ".")

        return fname

    @classmethod
    def save(cls, filename, *data_args, **kwargs):
        """Save data.

        data_args -- given to save_data
        kwargs -- given to get_fname
        """
        cls.assure_folder()
        full_filename = cls.get_fname(filename, **kwargs)
        cls.save_data(full_filename, *data_args)

        print("{} file saved to {}".format(cls.name, full_filename))

        if kwargs.get("ret_fname", False):
            return full_filename

    @classmethod
    def load(cls, filename, *data_args, **kwargs):
        """Load data.

        data_args -- given to load_data
        kwargs -- given to get_fname
        """
        filename = cls.get_fname(filename, **kwargs)

        try:
            result = cls.load_data(filename, *data_args)
            print("{} loaded from file: {}".format(cls.name, filename))
        except FileNotFoundError:
            basic.perror("{} file not found: {}".format(cls.name, filename))

        return result

    @classmethod
    def exist(cls, filename, **kwargs):
        """Boolean indicating if a file exist."""
        return os.path.isfile(cls.get_fname(filename, **kwargs))

    @classmethod
    def copy(cls, name1, name2):
        """Copy a file."""
        cls.assure_folder()
        filename1 = cls.get_fname(name1)
        filename2 = cls.get_fname(name2)

        shutil.copyfile(filename1, filename2)


    @classmethod
    def save_data(cls, filename, *data_args):
        ### OVERRIDE THIS FUNCTION ###
        pass

    @classmethod
    def load_data(cls, filename):
        ### OVERRIDE THIS FUNCTION ###
        pass
