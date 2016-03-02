from collections import namedtuple
from csv import writer, QUOTE_ALL
from hashlib import md5, sha256
from os import _exit, chown, listdir, mkdir, stat
from os.path import abspath, dirname, exists, isdir, isfile, join, relpath
from magic import from_file
from os import remove
from pwd import getpwnam
from shutil import copyfile
from sys import stdout, stderr
from treelib import Tree, Node
from uchicagoldr.filewalker import FileWalker
#from uchicagoldr.moveableitem import MoveableItem
from uchicagoldr.walktree import FileWalkTree
from datetime import datetime
from re import compile as re_compile

# === classes for moving files from one location to another ===

"""
1. ** FileProcessor ** is a super class. It shouldn't be called directly from application 
code. 
2. ** Stager ** is a sub-class of FileProcessor and it is meant to be called in application
 code that is intended to move a directory structure from an origin source into the ldr 
staging location. 
3. ** Archiver ** is a sub-class of FileProcessor. It should be called in an application 
that is tasked with moving a directory structure out of staging and into 
4. ** DataTransferObject ** is a class meant to hold data about files that can be written 
to a file on disk.
5. ** NewArchiver ** is a sub-class of FileProcessor. It should be used in applications that
are meant to move directories in staging that have premis records for every object in the 
directory.

"""

class FileProcessor(object):
    """
    == attributes ==
    1. filewalker is an instance of FileWalker
    2. tree is an instance of FileWalker tree

    == Args ==
    1. directory is the directory that needs to be walked and all the file contents 
    retrieved.
    2. source_root is a string representing the base of the origin file path that should 
    not be copied to the destination.

    == KWArgs ==
    1. irrelevant part is an optional argument to init a FileProcessor that will start a 
    tree with the substring of a string after the value of this kwarg.
    
    """
    def __init__(self, directory, source_root, irrelevant_part = None):
        """
        This initializes the FileProcessor with a call to the FileWalker that passes the 
        directory and creates a generator of a walk of the directory structure. A 
        FileWalkTree also gets created and the tree is populated with the directory 
        structure of the filewalker contents with files at the leaves.
        """
        self.filewalker = FileWalker(directory)
        self.tree = FileWalkTree()

        for n in self.filewalker:
            self.tree.add_node(n, irrelevant_parts = irrelevant_part)

    def find_all_files(self):
        """
        This function returns a list of all leaves in the filewalktree.
        """
        return self.get_tree().get_files()
            
    def find_directories_in_a_directory(self, a_node):
        """
        == Parameter ==
        1. a_node : a treelib.Node object

        This function takes a treelib.Node object, locates that node in the tree and 
        returns all branches of that node that are not leaves.
        """
        current_level = a_node
        subdirectories = [self.find_matching_node(x) for x in current_level.fpointer if not self.find_matching_node(x).is_leaf()]
        return subdirectories
        
    def pattern_matching_files_regex(self, regex):
        """
        == Args ==

        1. regex : a string representing a valid regular expression

        This function finds all leaves in the tree that have a tag that matches the regular
        expression entered.
        """
        matches = [x for x in self.get_tree().get_all_nodes() if \
                   re_compile(regex).search(x.tag) and x.is_leaf()]
        return matches
        
    def string_searching_files(self, val_string):
        """
        == Args ==

        1. val_string : a literal string

        This function finds all leaves in the tree that contain the literal string in the 
        tag name.
        """
        matches =  [x for x in self.get_tree().get_files() if
                    self.get_tree().find_string_in_a_node_tag(x, val_string)]
        return matches
    
    def string_searching_subdirectories(self, val_string):
        """
        == Parameters ==

        1. val_string: a literal string

        This function finds all nodes that are not leaves with the literal string in the 
        tag name.
        """
        matches = [x for x in self.get_tree().get_all_nodes() if
                   self.get_tree().is_it_a_subdirectory(x)]
        
        matches = [x for x in matches if self.get_tree(). \
                   find_string_in_a_node_tag(x, val_string)]
        return matches        

    def find_subdirectory_at_particular_level_down(self, val_string, level):
        """
        == Args == 
        1. val_string : a literal string
        2. level : integer

        This function finds all nodse that are not leaves matching a literal string at a 
        particular depth level entered.
        """
        level = int(level)
        potential_matches = self.string_searching_subdirectories(val_string)
        actual_matches = [x for x in potential_matches if self.get_tree().find_depth_of_a_node(x) == level]
        return actual_matches

    def find_matching_node(self, val_string):
        """
        == Parameters ==
        1. val_string : literal string

        This function returns either a single node that matches a specific identifier or 
        False if there are no nodes with that identifier or a ValueError if the 
        programmer has returned multiple tress with the same identifier.
        """
        matches = [x for x in self.get_tree().get_all_nodes() if self.get_tree().does_node_match_string(x, val_string)]
        if len(matches) > 1:
            raise ValueError("too many matches for that identifier")
        elif len(matches) == 0:
            return False
        return matches[0]

    def get_checksum(self, filepath):
        """
        == Parameters ==
        1. filepath : a string representing the absolute path to a file on-disk.

        This function takes a file path and returns an md5 checksum for that file.
        """
        blocksize = 65536
        md5_hash = md5()        
        file_run = open(filepath, 'rb')
        buf = file_run.read(blocksize)
        while len(buf) > 0:
            md5_hash.update(buf)
            buf = file_run.read(blocksize)
        file_run.close()
        return md5_hash.hexdigest()
    
    def find_file_in_a_subdirectory(self, a_node, file_name_string):
        """
        == Args == 
        1. a_node : a treelib.Node object
        2. file_name_string : a literal string

        This function returns True/False whether a leaf with the literal string in the 
        node identifier is below the node entered.
        """
        node = self.find_matching_node(a_node.identifier)
        if len([x for x in node.fpointer if file_name_string in x]) == 1:
            return True
        return False

    def find_files_in_a_subdirectory(a_node_name):
        return [x for x in self.find_matching_node(a_node_name).fpointer if x.is_leaf()]
    
    def get_tree(self):
        """
        This function returns the value of the tree attribute.
        """
        return self.tree

    def validate(self):
        """
        This method is left not implemented on FileProcessor. It must be defined for all 
        subclasses.
        """
        return NotImplemented

    def validate_files(self):
        """
        This method is left not implemented on FileProcessor. It must be defined for all 
        subclasses.
        """
        return NotImplemented

    def explain_validation_result(self):
        """
        This method is left not implemented on FileProcessor. It must be defined for all 
        subclasses.
        """
        return NotImplemented

class DataTransferObject(object):
    """
    == Attributes ==
    1. filepath should be a string representing a file path
    2. source should be a hexdigest string
    3. destination should be a hexdigest string
    4. moved  should be the letter 'Y' or 'N'
    5. uncorrupted should be the letter 'Y' or 'N'
    """
    def __init__(self, filep, source_checksum, destination_checksum, completed, uncorrupted):
        self.filepath = filep
        self.source = source_checksum
        self.destination = destination_checksum
        self.moved = completed
        self.uncorrupted = uncorrupted

    def write_to_manifest(self, manifestfile):
        """
        == Parameters ==
        1. manifestfile : a string representring a valid file path on disk of a text 
        file that can be modified.

        This function takes a string of a filepath on disk and writes the contents of 
        the DataTransferObject instance attributes to that file.
        """
        opened = open(manifestfile, 'a')
        opened.write("{}\t{}\t{}\t{}\t{}\n".format(self.filepath, self.source,
                                                   self.destination, self.moved,
                                                   self.uncorrupted))
        opened.close()
        
class Stager(FileProcessor):
    """
    == Attributes ==
    1. destination_root is the location that the Stager is supposed to move the origin 
       files to
    2. source_root is the base of the origin location of the files that need to be moved
    3. numfiles is the number of files in the origin location.
    4. prefix is a free-form string for a particular run that is part of a given staging 
    directory.
    5. staging_id is a free-form identifier for a staging directory. It is possible to 
       have multiple runs in a single staging location.
    
    """
    def __init__(self, directory, numfiles, stage_identifier, prefix, source_root, archive_directory):
        """
        == Args == 
        1. directory : literal string
        2. numfiles : integer
        3. staging_identifier : literal string
        4. prefix : literal string
        5. source_root : literal string
        6. archive_directory : literal string
        """
        FileProcessor.__init__(self, directory, source_root)
        self.destination_root = archive_directory
        self.source_root = source_root
        self.numfiles = numfiles
        self.prefix = prefix
        self.staging_id = stage_identifier

    def validate(self):
        """
        This is the validator function implemented for Stager class. This function 
        checks that the same number of files were found as was reported. If 
        the numbers are equal it returns true; if the numbers aren't equal it returns False.
        """
        numfilesfound = len(self.get_tree().get_files())
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
        if len(self.get_tree().get_files()) != self.numfiles:
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
        files = self.find_all_files()
        manifestfile = open(join(admin_dir, 'manifest.txt'),'r')
        manifestlines = manifestfile.readlines()
        manifestfiles = [x.split('\t') for x in manifestlines]
        manifestfiles = [x[0] for x in manifestfiles]
        new_files_to_ingest = [x for x in files if relpath(x.data.filepath, self.source_root) not in manifestfiles]
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
                
class Archiver(FileProcessor):

    """
    == Attributes ==

    1. prefix is a free-form string for describing a particular run in directory that needs to be archived
    2. numfolders is an integer representing the total number of runs represented in the driectory being archived
    3. numfiles is an integer representing the total number of files in the directory being archived
    4. source_root is the base of the origin of the files being archived
    5. destination_root is the base of the location to which the directory being archived should be moved
    6. destination_group is a name of a group that the archived files should belong
    7. destination_owner is the name of the user who sould own the archived files
    """    
    def __init__(self, directory, prefix, numfolders, numfiles,
                 source_root, archive_directory, group_id, user_id):

        FileProcessor.__init__(self, directory, source_root, irrelevant_part = source_root)
        self.prefix = prefix
        self.numfolders = numfolders
        self.numfiles = numfiles
        self.source_root = source_root
        self.destination_root = archive_directory
        self.destination_group = group_id
        self.destination_owner = user_id
        
    def validate(self):

        admin_node = self.find_subdirectory_at_particular_level_down('admin',3)
        data_node = self.find_subdirectory_at_particular_level_down('data', 3)

        if admin_node and data_node:
            subdirs_in_admin = self.find_directories_in_a_directory(admin_node.pop())
            subdirs_in_data = self.find_directories_in_a_directory(data_node.pop())
            if len(subdirs_in_data) == len(subdirs_in_admin) == self.numfolders:
                validate = True          
                for x in subdirs_in_admin:
                    find_fixity_files_in_admin = [x for x in subdirs_in_admin if 
                        self.find_file_in_a_subdirectory(x, 'fixityFromMedia.presform') and
                        self.find_file_in_a_subdirectory(x, 'fixityOnDisk.presform') and
                        self.find_file_in_a_subdirectory(x, 'rsyncFromMedia.presform')
                   ] 
                    if find_fixity_files_in_admin:
                        if len(subdirs_in_admin) == len(subdirs_in_data) == self.numfolders:
                            if self.numfiles == len(self.get_tree().get_files()):
                                return True
        return False
    
    def explain_validation_result(self):
        admin_node = self.find_subdirectory_at_particular_level_down('admin',3)
        data_node = self.find_subdirectory_at_particular_level_down('data', 3)
        if not admin_node:
            return namedtuple("ldrerror","category message")("fatal","missing \"admin\" folder in correct position in this directory")
        elif not data_node:
            return namedtuple("ldrerror","category message")("fatal","missing \"data\" folder in correct position in this directory")
        if admin_node and data_node:
            subdirs_in_admin = self.find_directories_in_a_directory(admin_node.pop())
            subdirs_in_data = self.find_directories_in_a_directory(data_node.pop())
            if len(subdirs_in_data) != len(subdirs_in_admin):
                return namedtuple("lderrror","category message")("fatal","subdirectories of data and admin are not equal in number")
            find_fixity_files_in_admin = [x for x in subdirs_in_admin if
                                          not self.find_file_in_a_subdirectory(x, 'fixityOnDisk.presform') or
                                          not self.find_file_in_a_subdirectory(x, 'fixityFromMedia.presform') or
                                          not self.find_file_in_a_subdirectory(x, 'mediaInfo.presform') or
                                          not self.find_file_in_a_subdirectory(x, 'rsyncFromMedia.presform')]
            if find_fixity_files_in_admin:
                return namedtuple("ldererror", "category message")("fatal", "the following foldesr in admin did not have a complete set of fixity files: {}".format(','.join([x.identifier for x in find_fixity_files_in_admin])))
        if len(self.get_tree().get_files()) != self.numfiles:
            return namedtuple("ldrerror", "category message")("fatal","There were {} files found in the directory, but you said there were supposed to be {} files".format(str(len(self.get_tree().get_files())),str(self.numfiles)))
        return True
    
    def validate_files(self):
        fixity_log_data = open(self.find_matching_files('fixityOnDisk.txt')[0], 'r').readlines() \
                          if self.find_matching_files('fixityOnDisk.txt') \
                             else None
        if not fixity_log_data:
            raise IOError("{} directory does not have a fixityOnDisk.txt file".format(self.filewalker.get_directory()))
        all_files = self.find_all_files()
        for x in all_files:
            line = [a for a in fixity_log_data if x.identifier in a]
            if line:
                fixity_log_checksum = line.split('\t')[0]
                if fixity_log_checksum == x.data.md5:
                    pass
                else:
                    raise IOError("{} had checksum {}".format(x.identifier,
                                                              fixity_log_checksum) + \
                                   " in fixityOnDisk.txt file and checksum {}".format(x.data.md5) + \
                                  " in staging directory")
        return True

    def ingest(self, flag=False):
        def copy_source_directory_tree_to_destination(filepath):
            destination_directories = dirname(filepath).split('/')
            if filepath[0] == '/':
                directory_tree = "/"
            else:
                directory_tree = ""
            for directory_part in destination_directories:
                directory_tree = join(directory_tree, directory_part)
                if not exists(directory_tree):
                    mkdir(directory_tree, 0o750)
                    
        if self.validate():
            files_to_ingest = (n for n in self.find_all_files())
            for n in files_to_ingest:
                source_file = n.data.filepath
                md5_checksum = n.data.checksum_md5
                sha256_checksum = n.data.checksum_sha256
                file_size = n.data.filesize
                file_mimetype = n.data.filemimetype
                destination_file = join(self.destination_root,
                                        relpath(n.data.filepath, self.source_root))
                copy_source_directory_tree_to_destination(destination_file)
                copyfile(source_file, destination_file)
                try:
                    chown(destination_file, self.destination_owner, self.destination_group)
                except Exception as e:
                    stderr.write("{}\n".format(str(e)))
                destination_md5 = self.get_checksum(destination_file)
                if not destination_md5 == md5_checksum:
                    manifestfile = open(join(destination_file, 'manifest.csv','a'))
                    manifestwriter = writer(manifestfile, delimiter=",",quoting=QUOTE_ALL)
                    manifestwriter.writerow([destination_file, destination_md5, source_md5, 'N', 'Y'])
                    manifestfile.close()                    
                    if flag:
                        pass
                    else:
                        raise IOError("{} destination file had checksum {}".format(destination_file, destination_checksum) + \
                                      " and source checksum {}".format(md5_checksum))
                else:
                    manifestfile = open(join(destination_file, 'manifest.csv','a'))
                    manifestwriter = writer(manifestfile, delimiter=",",quoting=QUOTE_ALL)
                    manifestwriter.writerow([destination_file, destination_md5, source_md5, 'Y', 'Y'])
                    manifestfile.close()
        else:
            problem = self.explain_validation_result()
            stderr.write("{}: {}\n".format(problem.category, problem.message))

class NewArchiver(FileProcessor):
    def __init__(self, directory, prefix, numfolders, numfiles,
                 source_root, archive_directory, group_id, user_id):

        FileProcessor.__init__(self, directory, source_root, irrelevant_part = source_root)
        self.prefix = prefix
        self.numfolders = numfolders
        self.numfiles = numfiles
        self.source_root = source_root
        self.destination_root = archive_directory
        self.destination_group = group_id
        self.destination_owner = user_id

    def validate(self):
        admin_node = self.find_subdirectory_at_particular_level_down('admin',1)
        data_node = self.find_subdirectory_at_particular_level_down('data', 1)
        valid_admin = False
        for n in admin_node:
            n_premis_present = False
            n_premis_match_with_data_files = False
            current= admin_node.pop()
            subdirs_in_current = self.find_directories_in_a_directory(current)
            if len(subdirs_in_current) == self.numfolders:
                valid_admin = True
            else:
                valid_admin = False
            n_premis_subdir_name = join(n.identifier,'premis')
            if self.find_subdirectory_at_a_particular_level_down(n_premis_subdir_name, 3):
                n_premis = True
            else:
                n_premis = False
            if n_premis:
                n_premis_file_count = len(self.find_files_in_a_subdirectory(n_premis_subdir_name))
                n_data_file_count = len(self.find_files_in_a_subdirectory(join('data',join(n.identifier.split('/')[-1]))))
                if n_premis_file_count == n_data_file_count:
                    n_premis_match_with_data_files = True
                else:
                    n_premis_match_with_data_files = False
        valid_data = False
        for n in data_node:
            current = data_node.pop()
            subdirs_in_current = self.find_directories_in_a_directory(current)
            if len(subdirs_in_current) == self.numfolders:
                valid_data = True
            else:
                valid_data = False
            if len(self.find_all_files()) == numfiles:
                numfiles_equals_files_supposed_to_be = True
            else:
                numfiles_equals_files_supposed_to_be = False
        return valid_admin & n_premis  & n_premis_match_with_data_files & valid_data & numfiles_equals_files_supposed_to_be

    def explain_validation_results(self):
        admin_node = self.find_subdirectory_at_particular_level_down('admin',1)
        data_node = self.find_subdirectory_at_particular_level_down('data', 1)
        valid_admin = False
        for n in admin_node:
            n_premis_present = False
            n_premis_match_with_data_files = False
            current= admin_node.pop()
            subdirs_in_current = self.find_directories_in_a_directory(current)
            if len(subdirs_in_current) != self.numfolders:
                return namedtuple("ldererror","category message") \
                    ("fatal","There are {} subdirectories in admin but there should be {}". \
                     format(str(len(subdirs_in_current)),str(args.numfolders)))

            n_premis_subdir_name = join(n.identifier,'premis')
            if not self.find_subdirectory_at_a_particular_level_down(n_premis_subdir_name, 3):
                return namedtuple("ldrerror", "category message") \
                    ("fatal","There is no premis directory in {}".format(n_premis_subdir_name))
            else:
    
                n_premis_file_count = len(self.find_files_in_a_subdirectory(n_premis_subdir_name))
                
                n_data_file_count = len(self.find_files_in_a_subdirectory(join('data',join(n.identifier.split('/')[-1]))))
                
                if n_premis_file_count != n_data_file_count:
                    current_prefix = n.identifier.split('/')[-1]
                
                    return namedtuple("ldrerror", "category message") \
                        ("fatal","There are {} premis files in {}".format(str(n_premis_file_count), current_prefix) + \
                         " and there are {} files in corresponding data directory".format(str(n_data_file_count)))
        
        for n in data_node:
            current = data_node.pop()
            subdirs_in_current = self.find_directories_in_a_directory(current)
            if len(subdirs_in_current) != self.numfolders:
                return namedtuple("ldererror","category message") \
                    ("fatal","There are {} subdirectories in data but there should be {}". \
                     format(str(len(subdirs_in_current)),str(args.numfolders)))
            if len(self.find_all_files()) != numfiles:
                return namedtuple("ldrerror", "category message") \
                         ("fatal","There are {} files but you said there should be {} files.".format(str(len(self.find_all_files())), args.numfolders))

    def ingest_premis_file(x):
        print(x)

    def ingest_data_file(x):
        print(x)
        
    def ingest(self):
        if self.validate():
    
            admin_node = self.find_subdirectory_at_particular_level_down('admin',1)
            data_node = self.find_subdirectory_at_particular_level_down('data', 1)
            for n in admin_node:
                current= admin_node.pop()
                subdirs_in_current = self.find_directories_in_a_directory(current)
                for i in subdirs_in_current:
                    current_premis_files = self.find_files_in_a_subdirectory(i)
                for p in current_premis_files:
                    ingest_premis_file(p.data.filepath)
            for n in data_node:
                current = data_node.pop()
                subdirs_in_current self.find_directories_in_a_directory(current)
                for i in subdirs_in_current:
                    current_data_files = self.find_directories_in_a_directory(i)
                for d in current_data_files:
                    ingest_data_file(d.data.filepath)
        else:
            return self.explain_validation_results()


class Pruner(FileProcessor):
    pattern_inputs = []
    patterns_compiled = []
    def __init__(self, directory, source_root, patterns):
        FileProcessor.__init__(self, directory, source_root, irrelevant_part = source_root)
        self.pattern_inputs = patterns

    def validate(self):
        for n in self.pattern_inputs:
            current_n = re_compile(n)            
            if len(self.pattern_matching_files_regex(current_n)) == 0:
                return False
        return True
    
    def explain_validation_result(self):
        for n in self.pattern_inputs:
            current_n = re_compile(n)
            if len(self.pattern_matching_files_regex(current_n)):
                return namedtuple("problem" "category message") \
                    ("fatal",
                     "The pattern {} does not match any files in the directory.".format(n))
        return namedtuple("problem", "category message") \
            ("non-fatal", "something something")

    def ingest(self):
        count = 0 
        for n in self.pattern_inputs:
            current_n = re_compile(n)
            matches = self.pattern_matching_files_regex(current_n)
            for m in matches:
                os.remove(m.data.filepath)
                count += 1
        return count
