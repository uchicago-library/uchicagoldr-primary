
from os.path import exists, join

from .ldrpath import LDRPath
__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ArchiveManifestWriter(object):
    def __init__(self, archive_location):
        self.manifest = archive_location
        self.lines = []

    def write(self):
        with self.manifest.open('ab') as writing_file:
            for line in self.lines:
                writing_file.write(bytes(line.encode('utf-8')))

    def add_a_line(self, filepath, digestdata):
        output_string = ""
        output_string += filepath
        for n_digest in digestdata.data:
            output_string += '\t' + n_digest.digest+'\n'
        self.lines.append(output_string)

    def get_manifest(self):
        return self._manifest

    def set_manifest(self, value):
        if not exists(value):
            raise ValueError(
                "{} archive loc for ArchiveManifestWriter".format(value) +
                " does not exist on the filesystem")
        else:
            manifest_filepath = join(value, 'manifest.txt')
            self._manifest = LDRPath(manifest_filepath)

    manifest = property(get_manifest, set_manifest)
