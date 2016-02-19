class FileWalker(object):
    items = []
    directory = None

    def __init__(self, directory_path, filter_pattern = None):
        self.directory = directory_path
        self.items = self.walk_directory(filter_pattern = filter_pattern)

    def __iter__(self):
        return self.items

    def get_directory(self):
        return self.directory
    
    def walk_directory(self, filter_pattern = None,
                        directory = None):
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

