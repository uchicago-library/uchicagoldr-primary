
from os import listdir
from os.path import abspath, exists

class FileProcessorInterface(object):

    def __init__(self, directory, directory_id, validation, validation_info,
                 source, destination, group_name=None):
        self._directory = directory
        self._validation_method = validation
        self._source_root = source
        self._destination_root = destination
        self._validation_info = validation_info        
        self._directory_id = directory_id
        if group_name:
            self._group_name = group_name


    def set_directory(self, value):
        if exists(abspath(value)):
            self._directory = value
        else:
            raise ValueError("{} does not exist".format(value))


    def get_directory(self):
        return self._directory


    def set_validation_method(self, value):
        if value not in ['staging', 'archiving']:
            raise ValueError("invalid validation method: {}".format(value))
        self._validation_method = value

    def get_validation_method(self):
        return self._validation_method


    def set_validation_info(self, value):
        self._validation_info = value


    def get_validation_info(self):
        return self._validation_info

    
    def set_source(self, value):
        if exists(abspath(value)):
            self._source_root = value
        else:
            raise ValueError("{} does not exist".format(value))

    def get_source(self):
        return self._source_root


    def set_destination(self, value):
        if exists(abspath(value)):
            self._destination_root = value
        else:
            raise ValueError("{} does not exist".format(value))
        

    def get_destination(self):
        return self._destination_root

    def set_directory_id(self, value):
        options = listdir(self.destination_root)
        if value in options:
            raise ValueError("{} is already in the destination {}".format(value, self.destination))
        else:
            self._directory_id = value

    def get_directory_id(self):
        return self._directory_id

    def get_group_name(self):
        return self._group_name

    def set_group_name(self, value):
        self._group_name = value


    
    directory = property(get_directory, set_directory)
    validation_method = property(get_validation_method, set_validation_method)
    validation_info = property(get_validation_info, set_validation_info)    
    destination_root = property(get_destination, set_destination)    
    source_root = property(get_source, set_source)
    directory_id = property(get_directory_id, set_directory_id)
    group_name = property(get_group_name, set_group_name)
    
        



    # def set_validation_info(self, value):
    #     self.validation_info = value

    # def get_validation_info(self):
    #     return self.validation_info

    # validation_info = property(get_validation_info, set_validation_info)
    # group_name = property(get_group_name, set_group_name)
    # directory_id = property(get_directory_id, set_directory_id)
    # destination_root = property(get_destination_root, set_destination_root)
    # source_root = property(get_source_root, set_source_root)
    # validation_method = property(get_validation_method, set_validation_method)


    # # fp = FileProcessor(args.directory, 'archiving', namedtuple("DirectoryInfo",
    # #                                               "src_root dest_root directory_id prefix " +\
    # #                                               "directory_type resume group_name validation")
    # #                    (args.source_root, args.destination_root, args.staging_id,
    # #                     args.prefix, 'archiving', args.resume,
    # #                     args.group,
    # #                     {'numfiles':args.numfiles, 'numfolders':args.numfolders}))
