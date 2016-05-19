from .materialsuite import MaterialSuite

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
