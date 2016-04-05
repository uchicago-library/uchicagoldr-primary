"""The DestinationFactory class should be used for instantiating the
right type of directory creator
"""

from internals.stagingdirectorycreator import StagingDirectoryCreator
from internals.archivingdirectorycreator import ArchivingDirectoryCreator

class DestinationFactory(object):
    """A factory class for creating particular directory creator objects
    """
    def __init__(self, kind):
        self.order = kind

    def build(self, info):
        """A method for building a particular directory creator
        """
        if self.order == 'staging':
            return StagingDirectoryCreator(info)
        elif self.order == 'archiving':
            return ArchivingDirectoryCreator(info)
        else:
            raise ValueError("unable to create that kind of object")
