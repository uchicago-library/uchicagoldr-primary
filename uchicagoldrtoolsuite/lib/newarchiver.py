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
