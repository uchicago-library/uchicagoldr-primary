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
