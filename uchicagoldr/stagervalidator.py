"""
The StagerValidator is used to determine whether the input given to a particular
instance of the Stager class is valid or not.
"""

from treelib import Tree


class StagerValidator(Validator):
    """The StagerValidator is a class that will test whether the given tree view
    of a potential stageable directory can be staged.
    """
    def __init__(self, necessary_info):
        self.data = necessary_info


    def test(self, snapshot: Tree) -> bool:
        """A function to test whether the given input is a valid directory to be staged.
        """
        number_of_files_found = len(snapshot.get_files())
        return bool(number_of_files_found == self.data.numfiles)


    def verbose_test(self, snapshot: Tree) -> str:
        """A function to test whether the given input is a valid directory and return
        an explanation of success/fail
        """
        number_of_files_found = len(snapshot.get_files())
        if number_of_files_found != self.data.numfiles:
            return "There were {} files actually found,".format(number_of_files_found) +\
                "but you said there should be {} files".format(self.data.numfiles)
        else:
            return "You said there were {}".format(self.data.numfiles) + \
                " files and there really were that number"

