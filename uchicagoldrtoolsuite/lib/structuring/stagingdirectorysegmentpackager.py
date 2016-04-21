
from .stagingsegmentpackager import StagingSegmentPackager
from .stagingdirectorymaterialsuitepackager import StagingDirectoryMaterialSuitePackager

class StagingDirectorySegmentPackager(StagingSegmentPackager):
    def __init__(self, label_text, label_number):
        self.struct_type = "staging"
        self.struct = "segment"
        self.implementation = "directory"
        self.msuite_packager = StagingDirectoryMaterialSuitePackager
        self.id_prefix = label_text
        self.id_num = label_number
        
    def get_material_suites(self):
        return []

    def package(self):
        return None

    def set_struct(self, value):
        self._struct = value

    def get_struct(self):
        return self._struct
    
    def set_msuite_packager(self, value):
        self._msuite_packager = value

    def get_msuite_packager(self):
        return self._msuite_packager

    def set_id_prefix(self, value):
        self._id_prefix = value

    def get_id_prefix(self):
        return self._id_prefix
    
    def set_id_num(self, value):
        self._id_num = value

    def get_id_num(self):
        return self._id_num    

    msuite_packager = property(get_msuite_packager, set_msuite_packager)
    id_prefix = property(get_id_prefix, set_id_prefix)
    id_num = property(get_id_num, set_id_num)
    struct = property(get_struct, set_struct)
    
# class SegmentPackager:

#     def create_segment(self, selected_items=[]):
#         segment_id = self.label_descripter+str(self.label_qualifier)
#         newsegment = SegmentStructure(self.label_descripter, segment_id)
#         if len(selected_items) > 0:    
#             just_files = self.segment_input.get_files()
#             all_nodes = self.segment_input.get_nodes()
#             just_directories = [x.identifier for x in all_nodes
#                                 if x.identifier not in just_files]


#             for n_thing in just_directories:
#                 a_file = LDRPathRegularDirectory(n_thing)
#                 msuite = MaterialSuiteStructure(a_file.item_name)
#                 msuite.original.append(a_file)
#                 newsegment.materialsuite.append(msuite)
#             for n_thing in just_files:
#                 a_file = LDRPathRegularFile(n_thing)
#                 msuite = MaterialSuiteStructure(a_file.item_name)
#                 msuite.original.append(a_file)
#                 newsegment.materialsuite.append(msuite)
#         else:
            
#             for n_item in selected_items:
#                 if is_file(n_item):
#                     a_thing = LDRPathRegularFile(n_file)
#                 else:
#                     a_thing = LDRPathRegularDirectory(n_item)
#                 msuite = MaterialSuite(a_thing)
#                 newsegment.materialsuite.append(msuite)
#         return newsegment
