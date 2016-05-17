from .materialsuite import MaterialSuite

class PresformMaterialSuite(MaterialSuite):

    required_parts = ['content', 'original', 'premis',
                      'technicalmetadata_list', 'presform_list', 'extension']

    def __init__(self):
        super().__init__()
        self._extension = None

    def get_extension(self):
        return self._extension

    def set_extension(self, x):
        self._extension = x

    extension = property(get_extension, set_extension)
