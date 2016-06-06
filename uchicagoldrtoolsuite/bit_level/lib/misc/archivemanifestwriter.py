
from os.path import exists, join

from .ldrpath import LDRPath

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ArchiveManifestWriter(object):
    """The ArchiveManifestWriter class is in charge of holding
    a file-like object for the archive manifest file and adding 
    archive file path and checksums for the file to the manifest
    """
    def __init__(self, archive_location):
        """initializes an ArchiveManifestWriter object
        
        __Args__
        1. archive_location (str): a file path string to a manifest
        file for the entire archive
        """
        self.manifest = archive_location
        self.lines = []

    def write(self):
        """serializes the contents of the lines data attribute to the LDR 
        file-like object representing the archive manifest file
        """
        with self.manifest.open('ab') as writing_file:
            for line in self.lines:
                writing_file.write(bytes(line.encode('utf-8')))

    def add_a_line(self, filepath, digestdata):
        """adds a file path and the checksums for that file to the lines 
        data attribute
        
        __Args__
        1. filepath (str) : a string pointing to a file in the archive with a 
        pair tree path
        2. digestdata (named tuple) : a named tuple object containing a list of named tuples
        namedtuple("digestdata", "data")([named tuple("digest", "algo digest")]
        """
        output_string = ""
        output_string += filepath
        for n_digest in digestdata.data:
            output_string += '\t' + n_digest.digest+'\n'
        self.lines.append(output_string)

    def get_manifest(self):
        """returns the mainfest data attribute
        """
        return self._manifest

    def set_manifest(self, value):
        """sets the manifest data attribute
        
        It takes the root to the archive location and sets the record data attribute 
        to point to an LDRPath to the manifest.txt file at root of the archive
        
        __Args__
        1. value (string): a string that is a the root to the ldr archive disk
        space
        """
        if not exists(value):
            raise ValueError(
                "{} archive loc for ArchiveManifestWriter".format(value) +
                " does not exist on the filesystem")
        else:
            manifest_filepath = join(value, 'manifest.txt')
            self._manifest = LDRPath(manifest_filepath)

    manifest = property(get_manifest, set_manifest)
