from os.path import split, relpath


class RootedPath(object):
    """
    This is a class meant to facilitate easy path manipulation for paths
    with different "roots" (the roots typically being the portions of
    a path leading up to a controlled directory structure, or a directory
    of particular interest).

    __Attributes__

    1. fullpath (str): the fullpath
    2. root (str): the root path
    3. path (str): The relpath from the root to the leaf
    """
    def __init__(self, path, root=None):
        """
        create an instance of a rooted path

        __Args__

        1. path (str): the fullpath
        2. root (str): the root of the fullpath, defaults to the containing
        dir of the leaf of the fullpath
        """
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
