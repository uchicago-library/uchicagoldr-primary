"""An abstract class for directory creator concrete classes
"""
class DirectoryCreator:
    """The DirectoryCreator abstract class should be used to create concrete
    directory creator classes with specific implementations
    """
    def create(self) -> None:
        """A method for creating a new directory according to a specific structure
        on-disk
        """
        raise NotImplementedError()

    def take_location(self, a_file) -> None:
        """A method meant to copy a file from source to the new directory
        """
        raise NotImplementedError()
