
class StagingProcessor(object):
    def __init__(self, directory):
        self.staging_directory = directory


class PremisBuilder(StagingProcessor):

    def __init__(self, directory):
        StagingProcessor.__init__(self, directory)

class Pruner(StagingProcessor):

    def __init__(self, directory, bad_files = []):
        StagingProcessor.__init__(self, directory)
        self.files_to_remove = bad_files

class FileConverter(StagingProcessor):

    def __init__(self, directory):
        StagingProcessor(self, directory)
        self.conversion_lookup = None

class TechnicalMetadataCreator(StagingProcessor):

    def __init__(self, directory):
        StagingProcessor(self, directory)

class Accessioner(StagingProcessor):

    def __init__(self, directory):
        StagingProcessor(self, directory)
        
