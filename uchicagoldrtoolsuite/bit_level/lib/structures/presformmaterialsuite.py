from json import dumps

from .materialsuite import MaterialSuite


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class PresformMaterialSuite(MaterialSuite):

    required_parts = ['content', 'original', 'premis',
                      'technicalmetadata_list', 'presform_list', 'extension']

    def __init__(self):
        super().__init__()
        self._extension = None

    def __repr__(self):
        attr_dict = {
            'content': str(self.get_content()),
            'premis': str(self.get_premis()),
            'extension': self.get_extension()
        }
        if self.technicalmetadata_list:
            attr_dict['technicalmetadata_list'] = [str(x) for x in self.technicalmetadata_list]
        else:
            attr_dict['technicalmetadata_list'] = None
        if self.presform_list:
            attr_dict['presform_list'] = [str(x) for x in self.presform_list]
        else:
            attr_dict['presform_list'] = None
        return "<PresformMaterialSuite {}>".format(dumps(attr_dict, sort_keys=True))

    def get_extension(self):
        return self._extension

    def set_extension(self, x):
        self._extension = x

    extension = property(get_extension, set_extension)
