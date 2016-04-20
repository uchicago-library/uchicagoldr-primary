
from .stagingdirectorymaterialsuitepackager import StagingDirectoryMaterialSuitePackager

class StagingDirectorySegmentPackager(StagingSegmentPackager):
    def __init__(self):
        self.struct_type = "staging"
        self.struct = "segment"
        self.implementation = "directory"
        self.msuite_packager = StagingDirectoryMaterialSuitePackager

    def get_material_suites(self):
        return []
    

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
