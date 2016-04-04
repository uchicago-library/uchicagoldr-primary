from uchicagoldr.rootedpath import RootedPath
from uchicagoldr.absolutefilepathtree import AbsoluteFilePathTree
from os.path import exists, normpath, split

class Stager(object):
    """description of class"""

    def __init__(self, rooted_path, numfiles, stage_identifier, prefix, source_root, archive_directory):
        if not isinstance(rooted_path, RootedPath):
            raise ValueError("Must instantiate a stager with a RootedPath")
        else:
            pass
        self.tree = AbsoluteFilePathTree(path=rooted_path, leaf_dirs=True)
        self.archive_directory = archive_directory
        self.source_root = source_root
        self.prefix = prefix
        self.stage_identifier = stage_identifier
        self.numfiles = numfiles

    def validate(self):
        """
        This is the validator function implemented for Stager class. This function
        checks that the same number of files were found as was reported. If
        the numbers are equal it returns true; if the numbers aren't equal it returns False.
        """
        leaves = self.tree.get_files()
        numfilesfound = len(leaves)
        if numfilesfound == self.numfiles:
            return True
        else:
            return False

    def explain_validation_result(self):
        """
        This is the explain validation results function implemented for Stager class. This
        function returns a namedtuple object with a category and a message explaining
        that the number of files found was not equal to the number reported.
        """
        if len(self.tree.get_files()) != self.numfiles:
            return namedtuple("ldrerror","category message")("fatal", "You said there were {} files, but {} files were found. This is a mismatch: please correct and try again.".format(str(self.numfiles),str(len(self.get_tree().get_files()))))
        else:
            return True

    def new_staging_directory(self):
        """
        This function returns a string joining the destination_root with the staging
id attribute values.
        """
        stage_id = self.staging_id
        return join(self.destination_root, stage_id)

    def new_staging_data_directory(self, stageID):
        """
        This function returns a string joining the destination root, the staging id
        and the string 'data'.
        """
        return join(self.destination_root, stageID, 'data')

    def new_staging_admin_directory(self, stageID):
        """
        This function returns a string joining the destination root, the staging id
        and the string 'admin'.
        """
        return join(self.destination_root, stageID, 'admin')

    def new_staging_data_with_prefix(self, stageID):
        """
        This function returns a string joining the destination root, the staging id,
        the string 'data' and a string consisting of the prefix and the number one.
        """
        data_directories = sorted(listdir(join(self.destination_root, stageID, 'data')))
        last_number = len(data_directories)
        new_number = str(last_number + 1)
        return join(self.destination_root, stageID, 'data', self.prefix+new_number)

    def new_staging_admin_with_prefix(self, stageID):
        """
        This function returns a string joining the destination root,
        the staging id, the string 'admin' and a string consisting of the
        prefix and the number one.
        """
        admin_directories = sorted(listdir(join(self.destination_root, stageID, 'admin')))
        last_number = len(admin_directories)
        new_number = str(last_number + 1)
        return join(self.destination_root, stageID, 'admin', self.prefix+new_number)

    def make_a_directory(self, directory_string):
        """
        == Args ==

        1. directory_string : literal string

        This function tries to create directory with a path delineated by the literal
        string. Before doing this, it checks if the directory already exists and returns
        the string "already" if it finds it. Otherwise, it returns the string "done" if the
        directory gets created or the string "invalid" if the system is unable to
        create the new directory.
        """
        if not exists(directory_string):
            try:
                mkdir(directory_string, 0o740)
                return "done"
            except IOError:
                return "invalid"
        else:
            return "already"

    def select_manifest_file(self, admin_directory):
        """
        == Args ==

        1. admin_directory : literal string

        This function tries to find a manifest.txt file in the literal string on disk.
        If it doesn't find it, it creates a new manifest.txt file with the required headers
        for the field that will be in that file . If it does find the file, it does
        nothing. Finally, the function returns a string representing the path to a
        manifest.txt file.
        """
        manifest_file = join(admin_directory, 'manifest.txt')
        if exists(manifest_file):
            pass
        else:
            opened_file = open(manifest_file, 'w')
            opened_file.write("filepath\torigin(md5)\tstaging(md5)\torigin==staging\twas moved\n")
            opened_file.close()

        return manifest_file

    def setup_fresh_staging_environment(self):
        """
        This function builds a new staging directory with all required subdirectories, and
        a first prefix directory in 'data' and 'admin' with a manifest.txt file in the first 'admin/prefix' directory. It returns a tuple containing a string representing the current data directory, a string representing the current admin directory and a string representing the manifest.xt file.

        """
        staging_directory = self.new_staging_directory()
        stageID = staging_directory.split('/')[-1]
        staging_data = self.new_staging_data_directory(stageID)
        staging_admin = self.new_staging_admin_directory(stageID)

        self.make_a_directory(staging_directory)
        self.make_a_directory(staging_data)
        self.make_a_directory(staging_admin)
        current_data_dir = self.new_staging_data_with_prefix(stageID)
        current_admin_dir = self.new_staging_admin_with_prefix(stageID)
        self.make_a_directory(current_data_dir)
        self.make_a_directory(current_admin_dir)
        manifestwriter = self.select_manifest_file(current_admin_dir)
        return (current_data_dir, current_admin_dir, manifestwriter)

    def add_to_a_staging_environment(self):
        """
        This function will create a new prefix directory in the 'admin' and 'data'
        directory for a new run in a previously built staging environment. It returns
        the newest data directory and the newest admin directory and the newest
        manifest.txt as a 3 tuple containing strings.
        """
        staging_directory = join(self.destination_root, self.staging_id)
        stageID = self.staging_id
        past_data_dirs = sorted(listdir(join(staging_directory, 'data')))
        prefix_data_dirs = [x for x in past_data_dirs if split(x)[1][:-1] == self.prefix]
        if prefix_data_dirs:
            last_data_dir_number = split(prefix_data_dirs[-1])[1].split(self.prefix)[1]
        else:
            last_data_dir_number = "0"
        new_data_dir_number = int(last_data_dir_number) + 1
        new_data_dir_with_prefix = self.prefix+str(new_data_dir_number)
        current_data_dir = join(staging_directory, 'data', new_data_dir_with_prefix)
        current_admin_dir = join(staging_directory, 'admin', new_data_dir_with_prefix)
        self.make_a_directory(current_data_dir)
        self.make_a_directory(current_admin_dir)
        manifestwriter = self.select_manifest_file(current_admin_dir)
        return (current_data_dir, current_admin_dir, manifestwriter)

    def pickup_half_completed_staging_run(self):
        """

        """
        staging_directory = join(self.destination_root, self.staging_id)
        past_data_dirs = sorted(listdir(join(staging_directory, 'data')))
        last_data_dir_number = self.prefix + str(past_data_dirs[-1].split(self.prefix)[1])
        current_data_dir = join(staging_directory, 'data', last_data_dir_number)
        current_admin_dir = join(staging_directory, 'admin', last_data_dir_number)
        manifestwriter = self.select_manifest_file(current_admin_dir)
        return (current_data_dir, current_admin_dir, manifestwriter)


    def get_files_to_ingest(self, admin_dir):
        """
        == Args ==

        1. admin_dir : literal string

        This function checks the admin directory specified for the manifest.txt file,
        reads the files added to that manifest already and finally finds the difference
        between files already transferred from origin and all files in the origin. Finally,
        it returns a list of files that still need to be copied from origin.
        """
        files = self.tree.get_files()
        manifestfile = open(join(admin_dir, 'manifest.txt'),'r')
        manifestlines = manifestfile.readlines()
        manifestfiles = [x.split('\t') for x in manifestlines]
        manifestfiles = [x[0] for x in manifestfiles]
        new_files_to_ingest = [x for x in files if relpath(x, self.source_root) not in manifestfiles]
        return new_files_to_ingest

    def ingest(self, ignore_mismatched_checksums = False,
               resume_partially_completed_run = False):
        """
        == Args ==

        1. ignore_mismatched_checksums : boolean
        2. resume_partially_completed_run : boolean

        This function is the implementation of ingest() for the Stager class. This
        function first checks if the Stager is valid, and if it is it will either create
        a new staging directory and copy origin files to the staging location or create
        a new prefix folder and copy files. It will also write the source and origin
        md5 checksums with the relative file path to the manifest.txt
        """

        def copy_source_directory_tree_to_destination(filepath):
            """
            == Args ==

            1. filepath : literal string

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
                if not exists(directory_tree):
                    mkdir(directory_tree, 0o740)

        if self.validate():
            if not exists(join(self.destination_root, self.staging_id)):
                current_data_directory, current_admin_directory, manifestwriter = \
                self.setup_fresh_staging_environment()
                files_to_ingest = self.get_files_to_ingest(current_admin_directory)
            elif resume_partially_completed_run:
                current_data_directory, current_admin_directory, manifestwriter = \
                self.pickup_half_completed_staging_run()
                files_to_ingest = self.get_files_to_ingest(current_admin_directory)
            else:
                current_data_directory, current_admin_directory, manifestwriter = \
                self.add_to_a_staging_environment()
                files_to_ingest = self.get_files_to_ingest(current_admin_directory)
        else:
            problem = self.explain_validation_result()
            stderr.write("{}: {}\n".format(problem.category, problem.message))
            _exit(2)

        for n in files_to_ingest:
            source_file = n.data.filepath
            destination_file = join(current_data_directory,
                                    relpath(n.data.filepath, self.source_root))

            copy_source_directory_tree_to_destination(destination_file)
            copyfile(source_file, destination_file)
            manifest_filepath = relpath(n.data.filepath, self.source_root)
            try:
                destination_md5 = self.get_checksum(destination_file)
                source_md5 = self.get_checksum(source_file)
                if destination_md5 == source_md5:
                    data_object = DataTransferObject(manifest_filepath,
                                              source_md5, destination_md5,'Y','Y')
                else:
                    data_object = DataTransferObject(manifest_filepath,
                                              source_md5, destination_md5, 'N','Y')
                    if ignore_mismatched_checksums:
                        pass
                    else:
                        raise IOError("{} destination file had checksum {}". \
                                      format(destination_file, destination_md5) + \
                                      " and source checksum {}".format(source_md5))
            except:
                data_object = DataTransferObject(manifest_filepath,"null","null","null","Y")
            data_object.write_to_manifest(manifestwriter)
