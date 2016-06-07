from os.path import join

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Pairtree(object):
    """This object is meant to take an identifier string and allow a user to
    convert that string into a valid pairtree path

    The path has three parts
    1. starts with the string constant "pairtree_root"
    2. identifier string broken into strings of length 2 with 1 appendeded
    to the last element if the total identifier string lenght is odd
    3. the constant "arf" which stands for Archival Resource Files which
    encapsulates the object

    __Attributes__
    1. pairtree_parts (list)
    2. pairtree_root (str constant)
    3. object_encapusluation (str constant)
    """
    def __init__(self, identifier_string):
        """returns a Pairtree object instance
        __Args__
        1. identifier_string (str): a string representing some identifier
        that needs to be transformed into a pairtree path
        """
        self.pairtree_parts = identifier_string
        self.pairtree_root = 'pairtree_root'
        self.object_encapsulation = 'arf'

    def set_object_encapsulation(self, value):
        """sets the object_encapsulation to "arf"
        """
        self._object_encapsulation = 'arf'

    def get_object_encapsulation(self):
        """returns the object encapsulation attribute
        """
        return self._object_encapsulation

    def set_pairtree_root(self, value):
        """sets the pairtree_roor attribute to "pairtree_root"
        """
        self._pairtree_root = 'pairtree_root'

    def get_pairtree_root(self):
        """returns the pairtree_root attribute
        """
        return self._pairtree_root

    def get_pairtree_path(self):
        """returns a valid pairtree path created with all of the attributes of
        the object instance
        """
        a_list = self.pairtree_parts
        first_part = join(self.pairtree_root, *a_list)
        return join(first_part, self.object_encapsulation)

    def get_pairtree_parts(self):
        """returns the pairtree_parts data attribute value
        """
        return self._pairtree_parts

    def set_pairtree_parts(self, value):
        """returns a list of strings of length 2

        __Args__
        1. value (str) : a string representing some identifier that needs to
        be converted into a pairtree
        """
        if len(value) % 2 > 0:
            output = value+'1'
        else:
            output = value
        output = [output[i:i+2] for i in range(0, len(output), 2)]
        self._pairtree_parts = output

    def __repr__(self):
        return "<{} ({} byte streams)>".format(self.pairtree_path)

    def __str__(self):
        return "{}".format(self.pairtree_path)

    object_encapsulation = property(get_object_encapsulation,
                                    set_object_encapsulation)
    pairtree_root = property(get_pairtree_root, set_pairtree_root)
    pairtree_parts = property(get_pairtree_parts, set_pairtree_parts)
