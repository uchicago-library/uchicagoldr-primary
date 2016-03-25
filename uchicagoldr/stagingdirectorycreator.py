"""The StagingDirectoryCreator class should only be called in the
DirectoryCreatorFactory
"""
from os import mkdir
from os.path import exists, join
from uchicagoldr.directorycreator import DirectoryCreator
from uchicagoldr.group import Group

class StagingDirectoryCreator(DirectoryCreator):
    """The StagingDirectoryCreator class is meant to create a valid staging directory
    and copy files from origin into the new staging directory
    """
    def __init__(self, info, group_name: str):
        self.info = info
        self.group = Group(group_name)


    def make_a_directory(self, directory_string: str):
        """
        == Args ==

        1. directory_string : literal string

        This function tries to create directory with a path delineated by the literal
        string. Before doing this, it checks if the directory already exists and returns
        the string "already" if it finds it. Otherwise, it returns the string "done" if 
        the directory gets created or the string "invalid" if the system is unable to
        create the new directory.
        """
        if not exists(directory_string):
            mkdir(directory_string, 0o740)
            self.group.change_location_group_ownership(directory_string)
        else:
            raise ValueError("cannot make directory {}".format(directory_string))


    def append_to_manifest(self, run: str) -> str:
        """A method to find and append run info to a manifest file
        """
        pass


    def create(self) -> bool:
        """A method to create a new staging directory
        """
        def make_directory(directory_name):
            """A method to try to make a directory and raise a ValueError if
            unable to create the directory.
            """
            try:
                self.make_a_directory(directory_name)
            except OSError:
                raise ValueError("could not make directory {}".format(base_directory))
            return True


        base_directory = join(self.info.dest_root, self.info.staging_id)
        admin_directory = join(base_directory, 'admin')
        data_directory = join(base_directory, 'data')
        accession_directory = join(base_directory, 'accessionrecord')
        legal_directory = join(base_directory, 'legal')
        notes_directory = join(base_directory, 'notes')
        make_directory(base_directory)
        make_directory(admin_directory)
        make_directory(data_directory)
        make_directory(accession_directory)
        make_directory(legal_directory)
        make_directory(notes_directory)
        return True


    def take_file(self, a_file) -> bool:
        """A method for copying a file from a source location into the
        new staging directory
        """
        return "not implemented"
