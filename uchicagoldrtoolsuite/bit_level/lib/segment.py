import re

from .abc.structure import Structure
from .materialsuite import MaterialSuite


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Segment(Structure):
    """
    The Segment holds materialsuites that are part of a segment of
    a larger structure. It validates to make sure that it only contains
    MaterialStructures
    1. label (str): a string of alphabetic characters
    2. run (int): an integer representing the order in the sequence that
       the segment was created
    3. identifier (str): a string combining the label and the run into a
       formal identification for the segment
    4. required_parts (list): a list of string representing the attributes
       on the class that must be present
       in order to consider this a valid instance of a structure
    5. materialsuite (list): a list of MaterialSuite instances that belong in
       the instance's segment

    """

    def __init__(self, param1, param2):
        self.label = param1
        self.run = param2
        self.identifier = param1+'-'+str(param2)
        self.required_parts = ['identifier', 'materialsuite', 'identifier']
        self.materialsuite = []

    def add_material_suite(self, x):
        self.materialsuite.append(x)

    def validate(self):
        for n_thing in self.materialsuite:
            if getattr(n_thing, MaterialSuite):
                pass
            else:
                return False
        return Structure._validate()

    def get_label(self):
        return self._label

    def set_label(self, value):
        if '-' in value:
            raise ValueError("The character '-' is protected in segment " +
                             "identifier parts.")
        else:
            self._label = value

    def get_run(self):
        return self._run

    def set_run(self, value):
        if isinstance(value, int):
            self._run = value
        else:
            raise ValueError("The value of run in segment structure " +
                             "must be an integer")

    def get_identifier(self):
        return self._identifier

    def set_identifier(self, value):
        if re.compile('^(\w{1,})[-](\d{1,})$').match(value):
            self._identifier = value
        else:
            raise ValueError("identifier for segment structure is not valid " +
                             "according to spec of [a-c]+-[0-9]+")

    label = property(get_label, set_label)
    run = property(get_run, set_run)
    identifier = property(get_identifier, set_identifier)
