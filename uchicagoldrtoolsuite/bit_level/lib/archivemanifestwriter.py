
from os.path import exists, join

from .ldrpath import LDRPath


class ArchiveManifestWriter(object):
    def __init__(self, archive_location):
        self.manifest = archive_location

    def write(self, filepath, digestdata):
        with self.manifest.open('ab') as writing_file:
            writing_file.write(self.write_a_line(filepath, digestdata))

    def write_a_line(self, filepath, digestdata):
        output_string = ""
        output_string += filepath
        for n_digest in digestdata.data:
            output_string += '\t' + n_digest.digest
        return output_string

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
