from json import dumps
from logging import getLogger

from .abc.structure import Structure
from .materialsuite import MaterialSuite


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


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

    required_parts = ['identifier', 'materialsuite', 'label', 'run']

    def __init__(self, label, run_no):
        self._label = None
        self._run = None
        self._materialsuite = []

        self.set_label(label)
        self.set_run(run_no)
        self.set_materialsuite_list([])
        log.debug("Segment spawned: {}".format(str(self)))

    def __repr__(self):
        attr_dict = {
            'identifier': self.identifier,
            'materialsuite_list': [str(x) for x in self.materialsuite_list]
        }
        return "<Segment {}>".format(dumps(attr_dict, sort_keys=True))

    def get_materialsuite_list(self):
        return self._materialsuite

    def set_materialsuite_list(self, materialsuite_list):
        self.del_materialsuite_list()
        for x in materialsuite_list:
            self.add_materialsuite(x)

    def del_materialsuite_list(self):
        while self.get_materialsuite_list():
            self.pop_materialsuite()

    def add_materialsuite(self, x):
        self._materialsuite.append(x)
        log.debug("Added MaterialSuite to Segment({}): {}".format(self.identifier, str(x)))

    def get_materialsuite(self, index):
        return self.get_materialsuite_list()[index]

    def pop_materialsuite(self, index=None):
        if index is None:
            x = self.get_materialsuite_list().pop()
        else:
            x = self.get_materialsuite_list().pop(index)
        log.debug("Popping MaterialSuite from Segment({}): {}".format(self.identifier, str(x)))

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
        log.debug("Setting Segment({}) label to {}".format(str(self.identifier), value))
        if '-' in value:
            raise ValueError("The character '-' is protected in segment " +
                             "identifier parts.")
        else:
            self._label = value

    def get_run(self):
        return self._run

    def set_run(self, value):
        log.debug("Setting Segment({}) run to {}".format(str(self.identifier), str(value)))
        if isinstance(value, int):
            self._run = value
        else:
            raise ValueError("The value of run in segment structure " +
                             "must be an integer")

    def get_identifier(self):
        # The identifier is a composite of the label and the run number
        # separated by a dash
        if self.label and self.run:
            return self.get_label() + "-" + str(self.get_run())
        else:
            return None

    materialsuite_list = property(get_materialsuite_list,
                                  set_materialsuite_list,
                                  del_materialsuite_list)
    label = property(get_label, set_label)
    run = property(get_run, set_run)
    identifier = property(get_identifier)
