from os.path import split, relpath


class RootedPath(object):
    def __init__(self, path, root=None):
        self.fullpath = path
        if root is None:
            self.root = split(path)[0]
        else:
            self.root = root
        if self.root not in split(path)[0]:
            raise ValueError('The root is not a subset of the path\n' +
                             'Path: {}\n'.format(path) +
                             'Root: {}'.format(root))
        self.path = relpath(path, start=self.root)
