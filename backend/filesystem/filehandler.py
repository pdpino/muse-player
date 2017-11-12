# DEPRECATED
# """Module that provides functionality to manage the data"""
# from enum import Enum
# import basic
#
# class FileType(Enum):
#     raw = 1
#     waves = 2
#     marks = 3
#     feelings = 4
#
#     def __str__(self):
#         if self == FileType.raw:
#             return "raw"
#         elif self == FileType.waves:
#             return "waves"
#         elif self == FileType.marks:
#             return "marks"
#         elif self == FileType.feelings:
#             return "feelings"
#         else:
#             return ""
#
# class DumpFileHandler(basic.FileHandler):
#     """Handle the dump file and folder names."""
#
#     """Folders."""
#     root_folder = "" # HERE
#     base_folder = "data"
#
#     """Extension."""
#     ext = "csv"
#
#     @classmethod
#     def get_subfolder(cls, tipo):
#         return str(tipo)
#
#     @classmethod
#     def get_fname(cls, name, subfolder=None, suffix=None, tipo=FileType.raw):
#         subfolder_type = cls.get_subfolder(tipo)
#         return cls._get_fname(name, folder=[subfolder_type, subfolder], suffix=suffix, ext=cls.ext)
#
#     @classmethod
#     def assure_folder(cls, subfolder, tipo):
#         cls._assure_folder(cls.get_subfolder(tipo), subfolder)
