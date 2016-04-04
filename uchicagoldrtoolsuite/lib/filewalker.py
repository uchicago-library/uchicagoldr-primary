from os import listdir
from os.path import isdir, isfile, join, relpath
from re import compile as re_compile

from uchicagoldrtoolsuite.lib.rootedpath import RootedPath

class FileWalker(object):
    """
    == Attributes ==

    1. items is an iterable containing all files found in a directory
    2. directory is a string representing a valid directory path on-disk
    """

    items = []
    directory = None

    def __init__(self, directory_path, filter_pattern=None, inc_dirs=False):
        """
        == Args ==

        1. directory_path : literal string
        2. filter_pattern : regular expression

        This class gets initialized with a directory path literal string and immediately defines the item attribute with the genexp of walking the directory for all files contained inside that directory path.
        """
        self.directory = directory_path
        self.items = self.walk_directory(filter_pattern=filter_pattern, inc_dirs=inc_dirs)

    def __iter__(self):
        """
        This function allows an application to call for n in FileWalker to iterate through all the files.
        """
        return self.items

    def get_directory(self):
        """
        This function returns the directory attached to the FileWalker instance.
        """
        return self.directory

    def walk_directory(self, directory=None, filter_pattern=None, inc_dirs=False):
        if directory is None:
            directory = self.get_directory()

        if isinstance(directory, str):
            return self._walk_abs_directory(directory, filter_pattern, inc_dirs)
        elif isinstance(directory, RootedPath):
            return self._walk_rooted_directory(directory, filter_pattern, inc_dirs)
        else:
            raise ValueError('dir not a str or RootedPath')

    def _walk_rooted_directory(self, directory, filter_pattern, inc_dirs):
        flat_list = listdir(directory.fullpath)
        while flat_list:
            node = flat_list.pop()
            fullpath = join(directory.fullpath, node)
            if isfile(fullpath):
                if filter_pattern:
                    if not re_compile(filter_pattern).search(fullpath):
                        continue
                yield relpath(fullpath, directory.root)
            elif isdir(fullpath):
                for child in listdir(fullpath):
                    flat_list.append(join(fullpath, child))
                if inc_dirs:
                    yield relpath(fullpath, directory.root)
            else:
                raise ValueError('not a file or a dir')

    def _walk_abs_directory(self, directory, filter_pattern, inc_dirs):
        """
        == KWArgs ==

        1. filter_pattern : regular expression
        2. directory : literal string

        This function walks the directory attribute value and optionally filters out files that match a determined filter pattern. It returns a genexp.
        """
        flat_list = listdir(directory)
        while flat_list:
            node = flat_list.pop()
            fullpath = join(directory, node)
            if isfile(fullpath):
                if filter_pattern:
                    if re_compile(filter_pattern).search(fullpath):
                        yield fullpath
                    else:
                        pass
                else:
                    yield fullpath
            elif isdir(fullpath):
                for child in listdir(fullpath):
                    flat_list.append(join(fullpath, child))
                if inc_dirs:
                    yield fullpath
            else:
                raise ValueError('not a file or a dir')
