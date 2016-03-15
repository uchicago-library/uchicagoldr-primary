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
