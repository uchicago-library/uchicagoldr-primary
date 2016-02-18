from os import remove
from uchicagoldr.filewalker import FileWalker
from uchicagoldr.tree import FileProcessor
        
class PremisBuilder(FileProcessor):
    def __init__(self, directory):
        StagingProcessor.__init__(self, directory)

class Pruner(FileProcessor):
    def prune():
        for a_file in self.tree.find_all_files():
            for a_pattern in self.superfluous_file_patterns:
                if re_compile(a_pattern).search(a_pattern):
                    remove(a_file)
        return 0
    
    def __init__(self, directory, bad_file_patterns):
        StagingProcessor.__init__(self, directory)
        self.superfluous_file_patterns = bad_file_patterns

class FileConverter(FileProcessor):

    def __init__(self, directory):
        StagingProcessor(self, directory)
        self.conversion_lookup = None

class TechnicalMetadataCreator(FileProcessor):

    def __init__(self, directory):
        StagingProcessor(self, directory)

class Accessioner(FileProcessor):

    def __init__(self, directory):
        StagingProcessor(self, directory)
        
