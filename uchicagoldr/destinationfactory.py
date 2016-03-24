class DestinationFactory(object):
    def __init__(self, kind):
        self.order = kind

    def build():
        if self.order == 'staging':
            return StagingDirectoryCreator()
        else:
            raise ValueError("unable to create that kind of object")
