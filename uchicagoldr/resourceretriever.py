from pkg_resources import Requirement, resource_filename
from controlledvocab.lib import ControlledVocabFromJson


class ResourceRetriever(object):
    def __init__(self):
        self.project = 'uchicagoldr'

    def get_filename_for_resource(resource_path):
        return resource_filename(
            Requirement.parse('uchicagoldr'), resource_path
        )

    def get_file_str(resource_path):
        x = None
        with open(self.get_filename_for_resource(resource_path), 'r') as f:
            x = f.read()
        return x

    def get_controlled_vocab(resource_path):
        fname = self.get_filename_for_resource(resource_path)
        cv = ControlledVocabFromJson(fname)
        return cv
