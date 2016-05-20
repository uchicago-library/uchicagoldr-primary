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
        repr_dict = {}
        repr_dict['content'] = self.get_content()
        repr_dict['premis'] = self.get_premis()
        repr_dict['technicalmetadata'] = self.get_technicalmetadata_list()
        repr_dict['presform'] = self.get_presform_list()
        repr_dict['extension'] = self.get_extension()
        return str(repr_dict)

    def get_extension(self):
        return self._extension

    def set_extension(self, x):
        self._extension = x

    extension = property(get_extension, set_extension)
