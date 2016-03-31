
class FileProcessorDirectoryInfo(object):
    def __init__(self, directory, validation_method, source, destination, destionation_id,
                 prefix, resumption_number, group_name, validation_info):
        self.directory = directory
        self.validation_method = validation_method
        self.source_root = source
        self.destination_root = destination
        self.directory_id = destination_id
        self.group_name = group_name
        self.validation_info = validation_info

    def set_directory(self, value):
        if exists(abspath(value)):
            self.directory = value
        else:
            raise ValueError("")


    def get_directory(self):
        return self.value

    def set_validation_method(self, value):
        if validation method in ['staging', 'archiving']:
            self.validation_method = value
        else:
            raise ValueError("invalid validation method being passed")

    def set_source_root(self, value):
        if exists(abspath(value)):
            self.source_root = value
        else:
            raise ValueError("cannot set source_root as a non-existent path")

    def get_source_root(self):
        return self.source_root

    def set_destination_root(self, value):
        if exists(abspath(value)):
            self.destination_root = value
        else:
            raise ValueError("cannot set source_root as a non-existent path")

    def get_destination_root(self):
        return self.destination_root


    def set_directory_id(self, value):
        if getattr(self, 'destination_root', None):
            destination_ids = listdir(self.destination_root)
            if value in destination_ids:
                raise ValueError("The directory id you entered conflicts with" +\
                                 " an existing directory id in the specified" +\
                                 " destination")
            else:
                self.directory_id = value
        else:
            raise ValueError("Must specify a destination root")
        
    def get_directory_id(self):
        return self.directory_id

    def get_group_name(self):
        return self.group_name

    def set_group_name(self, value):
        self.group_name = value

    def set_validation_info(self, value):
        self.validation_info = value

    def get_validation_info(self):
        return self.validation_info
                       
    fp = FileProcessor(args.directory, 'archiving', namedtuple("DirectoryInfo",
                                                  "src_root dest_root directory_id prefix " +\
                                                  "directory_type resume group_name validation")
                       (args.source_root, args.destination_root, args.staging_id,
                        args.prefix, 'archiving', args.resume,
                        args.group,
                        {'numfiles':args.numfiles, 'numfolders':args.numfolders}))
