from os.path import exists
from re import compile as re_compile

class LDRError(object):
    source = None
    label = ""
    message = ""

    def __init__(self, exception):
        assert isinstance(exception, Exception)
        self.source = exception
        self.label = exception.__name__
        self.message = exception.__message__
    
    def get_label(self):
        return self.label

    def get_message(self):
        return self.message

class Output(object):
    status = False
    error = None
    data  = None

    def __init_(self, type_string):
        if type_string in config['outputinformation']['valid_types']
            self.type = type_string
        else:
            self.type = None
        self.data = None

    def add_error(self, error_object):
        if self.error != None:
            return -1
        elif not isinstance(error_object, LDRError):
            return -1
        else:
            self.error = error_object
    
    def get_error(self):
        if self.error != None:
            return "{0}: {1}".format(self.error.get_label(),
                                     self.error.get_message())
    def get_status(self):
        return self.status

    def get_data(self):
        return self.data

    def add_data(self, data_object):
        if self.type != None data_object.__name__.lower() == self.type:
            self.data = data_object
            return 0
        else:
            return -1

    def display(self, record_format):
        if record_format in config['output_information']['valid_formats']:
            command = 'to_'+record_format
            return getattr(self.data.get_data(),command)()
 

class Batch(object):
    items = []
    def __init__(self):
        self.items = []

    def __iter__(self):
        return self.items
    
    def add_item(self, i):
        if isinstance(i, Item):
            self.items.append(item)
            return True
        else:
            return False
        
    def find_items(self, value):
        output = []
        for n in self:
            if value in n.filepath:
                output.append(value)
            else:
                pass
        return output

    def remove_items(self, i):
        if isinstance(i, Item):
            list_of_removeable_items = self.find_item(i.filepath)
            for n in list_of_removeable_items:
                index_of_item_to_remove = self.items.index(n)
                del self.items.pop(index_of_item_to_remove)
            return True  
        else:
            return False

    def get_item(self, value):
        search_list = self.find_item(value)
        num_results_in_search_list = len(search_list)
        if 0 < num_results_in_search_list <= 1:
            return search_list[0]
        else:
            return False
            

class Directory(Batch):
    directory_path = ""
    items = []

    def __init__(self, directory_path):
        if exists(directory_path):
            self.directory_path = directory_path
        else:
            raise IOError("{} does not exist on the file system.".format(directory_path))
        self.items = []

    def add_item(self, i):
        if isinstance(i, AccessionItem):
            self.items.append(i)
            return True
        return False

    def remove_items(self, i):
        if isinstance(i, AccessionItem):
            list_of_removeable_items = self.find_items(i.filepath)
            for n in list_of_removeable_items:
                index_of_items_to_remove = self.items.index(n)
                del self.items.pop(index_of_items_to_remove)
            return True
        else:
            return False

class FileWalker(object):
    def __init__(self):
        self.files = []

    def __iter__(self):
        return self.files
    
    def _create_generator(self, directory_path, filter_pattern=None):
        flat_list = listdir(self.directory_path)
        self.source_root = directory_path
        while flat_list:
            node = flat_list.pop()
            fullpath = join(self.directory_path, node)
            if isfile(fullpath):
                yield fullpath
            elif isdir(fullpath):
                for child in listdir(fullpath):
                    flat_list.append(join(fullpath, child))
        
    def walk_directory(self, directory_path):
        the_generator = self._create_generator(directory_path)
        self.files = the_generator

    def move_files(self, destination_path):
        for a_file in self.files:
            mi = MoveableItem(fullpath, self.source_root, destination_path)
            #mi.copy_into_new_location()
        
class DataValidator(Validator):
    def __init__(self):
        self.
        
class ValidatorFactory(object):
    def __init__(self, validate_type):
        self.engine = validate_type

    def build():
        if self.engine == 'admin':
            return AdminValidator()
        elif self.engine == 'data':
            return DataValidator()
        
class StagingDirectory(Directory):
    ark = ""
    ead = ""
    accno = ""
    data_path = ""
    admin_path = ""
    exists_on_disk = False
    ark_pattern = r"^\w{13}$"
    ead_pattern = r"^ICU[\.].*$"
    accno_pattern = r"^\d{4}[-]\d{3}$"
    prefix_pattern = r"[a-z]\w{1,}$"
    file_delegate = None
    validate_delegate = None
    
    def __init__(self, directory_path, destination_root,
                 ark, ead, accno, prefix):
        if exists(directory_path):
            self.directory_path = directory_path
            self.exists_on_disk = True
        else:
            self.exists_on_disk = False
        if not re_compile(ark_pattern).match(ark):
            raise ValueError("{} is not a valid ark identifier.".format(ark))
        if not re_compile(ead_pattern).match(ead):
            raise ValueError("{} is not a valid ead identifier.".format(ead))
        if not re_compile(accno_pattern).match(accno):
            raise ValueError("{} is not a valid accno identifier.".format(accno))
        if not re_compile(prefix_pattern).match(prefix):
            raise ValueError("prefix {} needs to be a string alphanumeric" + \
                             " characters starting with any character" + \
                             "between a and z")
        
        self.ark = ark
        self.ead = ead
        self.accno = accno
        self.prefix = prefix
        self.final_destination = destination_root
        self.file_delegate = FileWalker()
        self.file_delegate.walk_directory(self.directory_path)
        self.validate_admin = ValidatorFactory('admin')
        self.validate_data = ValidatorFactory('data')
                
    def validate():
        self.data_validator.validate()
        self.admin_validator.validate()
        
    
    def audit():
        self.data_validator.validate()
        self.admin_validator.validate()
    
    def ingest():
        self.audit()
        self.file_delegate.move_files(self.final_destination)

