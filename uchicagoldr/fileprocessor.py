from uchicagoldr.absolutefilepathtree import AbsoluteFilePathTree


class FileProcessor(object):
    def __init__(self, path):
        self.tree = AbsoluteFilePathTree(path)
