from os import remove
from uchicagoldr.bash_cmd import BashCommand
from uchicagoldr.filewalker import FileWalker
from uchicagoldr.tree import FileProcessor
        
class PremisBuilder(FileProcessor):
    def __init__(self, directory):
        StagingProcessor.__init__(self, directory)

class Pruner(FileProcessor):
    def prune():
        for a_pattern in self.superfluous_file_patterns:
            files_to_delete = self.pattern_matching_files_regex(a_pattern)
            if len(files_to_delete) > 0:
                for a_file in files_to_delete:
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

    def generate_technical_metadata(self, a_file_string):
        output_option = "-i {}".format(a_file_string+'.fits.xml')
        bcmd = BashCommand(['/usr/app/acc/fits/fits.sh',
                            '-i {}'.format(a_file_string),
                            "-o {}".format(output_option),
                            "-x"])
        bcmd.run_command()
        return bcmd.get_data()
    
    def __init__(self, directory):
        FilePorcessor.__init__(self, directory)


# class Accessioner(FileProcessor):
#     def __init__(self, directory):
#         FileProcessor.__init__(self, directory)
#         self.record = None

#     def buildAcqRecord(self):
        
