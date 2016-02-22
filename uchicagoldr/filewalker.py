class FileWalker(object):
    """
    == Attributes ==

    1. items is an iterable containing all files found in a directory
    2. directory is a string representing a valid directory path on-disk
    """
    
    items = []
    directory = None

    def __init__(self, directory_path, filter_pattern = None):
        """
        == Args ==

        1. directory_path : literal string
        2. filter_pattern : regular expression

        This class gets initialized with a directory path literal string and immediately defines the item attribute with the genexp of walking the directory for all files contained inside that directory path.
        """
        self.directory = directory_path
        self.items = self.walk_directory(filter_pattern = filter_pattern)

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
    
    def walk_directory(self, filter_pattern = None,
                        directory = None):
        """
        == KWArgs ==

        1. filter_pattern : regular expression
        2. directory : literal string

        This function walks the directory attribute value and optionally filters out files that match a determined filter pattern. It returns a genexp.
        """
        from os import listdir, walk
        from os.path import isdir, isfile, join
        from re import compile as re_compile
        if not directory:
            directory = self.directory
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

