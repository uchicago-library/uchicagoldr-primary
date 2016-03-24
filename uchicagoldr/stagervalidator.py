"""
The StagerValidator is used to determine whether the input given to a particular
instance of the Stager class is valid or not.
"""

from treelib import Tree
from uchicagoldr.validator import Validator

class StagerValidator(Validator):
    """The StagerValidator is a class that will test whether the given tree view
    of a potential stageable directory can be staged.
    """
    def __init__(self, necessary_info):
        self.data = necessary_info
        self.rules = [lambda x: x == necesary_info.numfiles]

    def _is_required_info_present(self) -> bool:
        """A method to check if the validator has all the information it needs 
        to make its decision
        """
        if not getattr(self.data.numfiles, None) and getattr(self.data.numfilesfound, None):
            raise ValueError("missing required information to validate this directory")
        return True
        
    def test(self, processor_info: dict) -> bool:
        """A function to test whether the given input is a valid directory to be staged.
        """
        _is_required_info_present()
        numfilesfound = processor_info.get('numfilesfound')
        return self.data.numfiles == numfilesfound

    def get_info_needed(self):
        return ['numfilesfound':int]

    def verbose_test(self, processor_info: dict) -> str:
        """A function to test whether the given input is a valid directory and return
        an explanation of success/fail
        """
        _is_required_info_present(self)
        numfilesfound = processor_info.get('numfilesfound')
        if self.data.numfiles != numfilesfound:
            return ("fatal", "There were {} files actually found,".format(number_of_files_found) +\
                "but you said there should be {} files".format(self.data.numfiles))
        else:
            return ("info", "You said there were {}".format(self.data.numfiles) + \
                " files and there really were that number")
