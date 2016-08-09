from os import scandir
from os.path import relpath
from re import compile as re_compile

from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from .rootedpath import RootedPath


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)


class FileWalker(object):
    """
    == Attributes ==

    1. items is an iterable containing all files found in a directory
    2. directory is a string representing a valid directory path on-disk
            - or -
       and instance of RootedPath
    """

    items = []
    directory = None

    def __init__(self, directory_path, filter_pattern=None, inc_dirs=False):
        """
        == Args ==

        1. directory_path : literal string or RootedPath instance
        2. filter_pattern : regular expression

        This class gets initialized with a directory path literal string and
        immediately defines the item attribute with the genexp of walking the
        directory for all files contained inside that directory path.
        """
        log.debug(
            "FileWalker spawned. " +
            "Path = {}. Filter Pattern = {}. Inc_dirs = {}".format(
                directory_path, str(filter_pattern), str(inc_dirs)
            )
        )
        self.directory = directory_path
        self.filter_pattern = filter_pattern
        self.inc_dirs = inc_dirs
        self.items = self.walk_directory()

    def __iter__(self):
        """
        This function allows an application to call for n in FileWalker to
        iterate through all the files.
        """
        return self.items

    def get_directory(self):
        """
        This function returns the directory attached to the FileWalker instance.
        """
        return self.directory

    def walk_directory(self, directory=None, filter_pattern=None,
                       inc_dirs=None):
        if directory is None:
            directory = self.get_directory()
        if filter_pattern is None:
            filter_pattern = self.filter_pattern
        if inc_dirs is None:
            inc_dirs = self.inc_dirs

        if filter_pattern is not None:
            filter_pattern = re_compile(filter_pattern)

        if isinstance(directory, str):
            return self._walk_abs_directory(directory, filter_pattern, inc_dirs)
        elif isinstance(directory, RootedPath):
            return self._walk_rooted_directory(directory, filter_pattern,
                                               inc_dirs)
        else:
            raise ValueError('dir not a str or RootedPath')

    def _walk_rooted_directory(self, directory, filter_pattern, inc_dirs):
        flat_list = [x for x in scandir(directory.fullpath)]
        while flat_list:
            node = flat_list.pop()
            if node.is_file():
                if filter_pattern:
                    if not filter_pattern.search(node.path):
                        continue
                yield relpath(node.path, directory.root)
            elif node.is_dir():
                for child in scandir(node.path):
                    flat_list.append(child)
                if inc_dirs:
                    yield relpath(node.path, directory.root)
            else:
                raise ValueError('not a file or a dir')

    def _walk_abs_directory(self, directory, filter_pattern, inc_dirs):
        """
        == KWArgs ==

        1. filter_pattern : regular expression
        2. directory : literal string

        This function walks the directory attribute value and optionally
        filters out files that match a determined filter pattern. It returns
        a genexp.
        """
        flat_list = [x for x in scandir(directory)]
        while flat_list:
            node = flat_list.pop()
            if node.is_file():
                if filter_pattern:
                    if filter_pattern.search(node.path):
                        yield node.path
                    else:
                        pass
                else:
                    yield node.path
            elif node.is_dir():
                for child in scandir(node.path):
                    flat_list.append(child)
                if inc_dirs:
                    yield node.path
            else:
                raise ValueError('not a file or a dir')
