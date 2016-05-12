from os.path import join

from .ldritemoperations import duplicate_ldritem, pairtree_a_string
from .abc.ldritem import LDRItem

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Pairtree(object):
    def __init__(self, identifier_string):
        self.pairtree_parts = pairtree_a_string(identifier_string)
        self.pairtree_root = 'pairtree_root'
        self.object_encapsulation = 'arf'
        self.pairtree_path = 'doesn\'t matter what I type here'
        self.contents = []
        self.content_index = 0

    def set_contents(self, value):
        if not isinstance(value, LDRItem):
            raise TypeError("pairtree contents must be an ldr item")
        if self.contents == []:
            self._contents = [value]
        else:
            already_added = False
            for n_item in self._contents:
                if duplicate_ldritem(n_item, value):
                    break
            if not already_added:
                self._contents.append(value)

    def get_contents(self):
        return self._contents

    def set_object_encapsulation(self, value):
        self._object_encapsulation = 'arf'

    def get_object_encapsulation(self):
        return self._object_encapsulation

    def set_pairtree_root(self, value):
        self._pairtree_root = 'pairtree_root'

    def get_pairtree_root(self):
        return self._pairtree_root

    def set_pairtree_path(self, value):
        self._pairtree_path = join(self.pairtree_root, *self.pairtree_parts,
                                   self.object_encapsulation)

    def get_pairtree_path(self):
        return self._pairtree_path

    def __repr__(self):
        return "<{} ({} byte streams)>".format(self.pairtree_path,
                                               len(self.contents))

    def __str__(self):
        return "{}".format(self.pairtree_path)

    def __iter__(self):
        return self.contents

    def __next__(self):
        try:
            result = self.contents[self.content_index]
        except IndexError:
            raise StopIteration
        self.content += 1
        return result

    contents = property(get_contents, set_contents)
    object_encapsulation = property(get_object_encapsulation,
                                    set_object_encapsulation)
    pairtree_root = property(get_pairtree_root, set_pairtree_root)
    pairtree_path = property(get_pairtree_path, set_pairtree_path)
    contents = property(get_contents, set_contents)
