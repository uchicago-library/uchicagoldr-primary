class LeafData(object):
    """
    == Attributes ==

    1. filepath
    2. filesize

    """

    def __init__(self, filepath):
        if not exists(filepath):
            raise IOError("{} directory must exist on disk.".format(filepath))
        if filepath[0] != '/':
            self.filepath = abspath(filepath)
        else:
            self.filepath = filepath
        self._derive_filesize()

    def get_filepath(self):
        """
        This function returns the value of the filepath attribute.
        """
        return self.filepath

    def get_filesize(self):
        """
        This function returns the value of the filesize attribute.
        """
        return self.filesize

    def _derive_filesize(self):
        """
        This function extracts the size of the file and sets it to the filesize attribute.
        """
        from os import stat
        self.filesize = stat(self.filepath).st_size

    def _derive_filemimetype(self):
        """
        This function extracts the mimetype of the file one of 2 ways: either from the
        file extension or magic numbers but it prefers the magic numbers evaluation. It
        then sets the filemimetype attribute.
        """
        try:
            mimetype = guess_type(self.filepath)
        except Exception as e:
            mimetype = None
        try:
            mimetype = from_file(self.filepath, mime=True).decode('utf-8')
        except Exception as e:
            mimetype = None
        self.filemimetype = mimetype

    def __repr__(self):
        return self.filepath
