"""The StagingDirectoryCreator class should only be called in the
DirectoryCreatorFactory
"""
from os import listdir, mkdir
from os.path import dirname, exists, join, relpath
from shutil import copyfile
from uchicagoldr.directorycreator import DirectoryCreator
from uchicagoldr.group import Group


class StagingDirectoryCreator(DirectoryCreator):
    """The StagingDirectoryCreator class is meant to create a valid staging
    directory and copy files from origin into the new staging directory
    """
    def __init__(self, info, group_name: str, resume=False):
        self.destination_root = info.dest_root
        self.source_root = info.source_root
        self.stage_id = info.staging_id
        self.prefix = info.prefix
        self.group = Group(group_name)
        if not resume:
            self.current_run = self.prefix + '1'
        else:
            try:
                listdir(join(self.destination_root, self.stage_id, 'data'))[-1]
            except IndexError:
                raise ValueError("you are trying to resume a staging " +\
                                 " directory creation but there doesn't " +\
                                 "appear to be a prior run in 'data' directory")
            self.current_run = self.prefix + '2'


    def make_a_directory(self, directory_string: str):
        """A method to make a directory on-disk and raise a ValueError if
        unable to do so

        __Args__

        :param directory_string: str

        :rtype None

        This function tries to create directory with a path delineated by the
        literal string. Before doing this, it checks if the directory already exists
        and returns the string "already" if it finds it. Otherwise, it returns the
        string "done" if the directory gets created or the string "invalid" if
        the system is unable to create the new directory.
        """
        if not exists(directory_string):
            mkdir(directory_string, 0o740)
            self.group.change_location_group_ownership(directory_string)
        else:
            raise ValueError("cannot make directory {}".format(directory_string))


    def create(self) -> bool:
        """A method to create a new staging directory

        :rtype bool
        """
        def make_directory(directory_name):
            """A method to try to make a directory and raise a ValueError if
            unable to create the directory.

            __Args__
            :param directory_name: str

            :rtype bool
            """
            try:
                self.make_a_directory(directory_name)
            except OSError:
                raise ValueError("could not make directory {}".format(base_directory))
            return True


        base_directory = join(self.destination_root, self.stage_id)
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


    def take_location(self, a_file) -> bool:
        """A method for copying a file from a source location into the
        new staging directory

        __Args__

        :param a_file: str

        :rtype bool
        """
        def copy_source_directory_tree(filepath) -> str:
            """A method to build out a directory tree on-disk

            __Args__

            :param filepath: str

            :rtype None

            This function takes a literal string and chops off the filename portion
            and recreate the directory structure of origin file in the destination
            location.
            """
            destination_directories = dirname(filepath).split('/')
            if filepath[0] == '/':
                directory_tree = "/"
            else:
                directory_tree = ""
            for directory_part in destination_directories:
                directory_tree = join(directory_tree, directory_part)
                self.make_a_directory(directory_tree)


        def append_to_manifest(self, relative_filepath: str, md5_hash: str) -> bool:
            """A method to find and append run info to a manifest file

            :rtype str
            """
            manifest_directory = join(self.destination_root, self.staging_id,
                                      'admin', self.current_run)
            manifest_file = join(manifest_directory, 'manifest.txt')
            if exists(manifest_file):
                opened_file = open(manifest_file, 'a')
            else:
                opened_file = open(manifest_file, 'w')
            manifest_string_line = "{}\t{}".format(md5_hash,
                                                   relative_filepath)
            opened_file.write(manifest_string_line)
            opened_file.close()
            return True


        if getattr(a_file, 'type', None):
            item_type = a_file.type
        else:
            raise ValueError("invalid object passed to take_location()." +\
                             "object must have a 'type' attribute")
        filepath_to_care_about = relpath(a_file, self.source_root)
        new_full_file_path = join(self.destination_root, self.stage_id,
                                  'data', self.current_run, filepath_to_care_about)
        if item_type == 'directory':
            copy_source_directory_tree(new_full_file_path)
        elif item_type == 'file':
            copyfile(join(self.source_root, filepath_to_care_about),
                     new_full_file_path)
            append_to_manifest(filepath_to_care_about, a_file.md5, self.current_run)
        else:
            raise ValueError("passed wrong type of object passed " +\
                             " to take_a_location: object must be either " +\
                             " type=directory or type=filepath")
        return filepath_to_care_about
