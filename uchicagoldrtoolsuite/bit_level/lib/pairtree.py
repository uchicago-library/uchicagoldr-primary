from os.path import join

from .ldritemoperations import pairtree_a_string

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

    def set_object_encapsulation(self, value):
        self._object_encapsulation = 'arf'

    def get_object_encapsulation(self):
        return self._object_encapsulation

    def set_pairtree_root(self, value):
        self._pairtree_root = 'pairtree_root'

    def get_pairtree_root(self):
        return self._pairtree_root

    def get_pairtree_path(self):
        return join(self.pairtree_root, *self.pairtree_parts,
                    self.object_encapsulation)

    def __repr__(self):
        return "<{} ({} byte streams)>".format(self.pairtree_path)

    def __str__(self):
        return "{}".format(self.pairtree_path)

    object_encapsulation = property(get_object_encapsulation,
                                    set_object_encapsulation)
    pairtree_root = property(get_pairtree_root, set_pairtree_root)
