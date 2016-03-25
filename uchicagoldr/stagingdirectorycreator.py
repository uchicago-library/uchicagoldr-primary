"""The StagingDirectoryCreator class should only be called in the
DirectoryCreatorFactory
"""

from uchicagoldr.directorycreator import DirectoryCreator

class StagingDirectoryCreator(DirectoryCreator):
    """The StagingDirectoryCreator class is meant to create a valid staging directory
    and copy files from origin into the new staging directory
    """
    def __init__(self, info):
        self.info = info

    def create(self):
        """A method to create a new staging directory
        """
        return "not implemented"

    def take_file(self, a_file):
        """A method for copying a file from a source location into the
        new staging directory
        """
        return "not implemented"
