from .abc.converter import Converter

class OfficeToPDFConverter(Converter)

    _claimed_mimes = []

    def __init__(self, target_path, target_premis_path):
       super().__init__(target_path, target_premis_path)

    def convert(self):



