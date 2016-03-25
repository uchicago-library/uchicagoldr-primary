"""
The StagerValidator is used to determine whether the input given to a particular
instance of the Stager class is valid or not.
"""

from uchicagoldr.validator import Validator

class StagerValidator(Validator):
    """The StagerValidator is a class that will test whether the given tree view
    of a potential stageable directory can be staged.
    """
    def __init__(self, necessary_info):
        self.data = necessary_info

    def is_required_info_present(self) -> bool:
        """A method to check if the validator has all the information it needs
        to make its decision
        """
        if not getattr(self.data.numfiles, None) and getattr(self.data.numfilesfound, None):
            return False
        return True

    def test(self, processor_info: dict) -> bool:
        """A function to test whether the given input is a valid directory to be staged.
        """
        self.is_required_info_present()
        numfilesfound = processor_info.get('numfilesfound')
        return self.data.numfiles == numfilesfound

    def get_info_needed(self):
        return {'numfilesfound':int}


    def verbose_test(self, processor_info: dict) -> str:
        """A function to test whether the given input is a valid directory and return
        an explanation of success/fail
        """
        self.is_required_info_present(self)
        number_of_files_found = processor_info.get('numfilesfound')
        if self.data.numfiles != number_of_files_found:
            return ("fatal", "There were {} files actually found,".format(number_of_files_found) +\
                "but you said there should be {} files".format(self.data.numfiles))
        else:
            return ("info", "You said there were {}".format(self.data.numfiles) + \
                " files and there really were that number")
