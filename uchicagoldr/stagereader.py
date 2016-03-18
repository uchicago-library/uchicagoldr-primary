from os.path import join
from re import sub
from re import compile as re_compile

from uchicagoldr.filepathtree import FilePathTree
from uchicagoldr.rootedpath import RootedPath


class StageReader(object):

    re_trailing_numbers = re_compile('[0-9]+$')

    def __init__(self, rootedpath):
        if not isinstance(rootedpath, RootedPath):
            raise ValueError()

        self.fpt = FilePathTree(rootedpath, leaf_dirs=True)

        self.root_node = self.fpt.tree.root
        self.root_fullpath = rootedpath.root

        self.stage_id_path = rootedpath.path
        self.stage_id_node = self.fpt.find_tag_at_depth(self.stage_id_path, 1)
        self.stage_id_fullpath = rootedpath.fullpath

        self.admin_node = self.fpt.tree.get_node(join(self.stage_id_path, 'admin'))
        self.admin_path = self.admin_node.identifier
        self.admin_fullpath = join(self.root_fullpath, self.admin_path)

        self.data_node = self.fpt.tree.get_node(join(self.stage_id_path, 'data'))
        self.data_path = self.data_node.identifier
        self.data_fullpath = join(self.root_fullpath, self.data_path)

        self.notes_node = self.fpt.tree.get_node(join(self.admin_path, 'notes'))
        self.notes_path = self.notes_node.identifier
        self.notes_fullpath = join(self.root_fullpath, self.notes_path)

        self.note_nodes = [self.fpt.tree.get_node(x) for x in self.notes_node.fpointer]
        self.note_paths = [x.identifier for x in self.note_nodes]
        self.note_fullpaths = [join(self.root_fullpath, x) for x in self.note_paths]

        self.legal_node = self.fpt.tree.get_node(join(self.admin_path, 'legal'))
        self.legal_path = self.legal_node.identifier
        self.legal_fullpath = join(self.root_fullpath, self.legal_path)

        self.legal_nodes = [self.fpt.tree.get_node(x) for x in self.legal_node.fpointer]
        self.legal_paths = [x.identifier for x in self.legal_nodes]
        self.legal_fullpaths = [join(self.root_fullpath, x) for x in self.legal_paths]

        self.accession_records_node = self.fpt.tree.get_node(join(self.admin_path, 'accession_records'))
        self.accession_records_path = self.accession_records_node.identifier
        self.accession_records_fullpath = join(self.root_fullpath, self.accession_records_path)

        self.accession_record_nodes = [self.fpt.tree.get_node(x) for x in self.accession_records_node.fpointer]
        self.accession_record_paths = [x.identifier for x in self.accession_record_nodes]
        self.accession_record_fullpaths = [join(self.root_fullpath, x) for x in self.accession_record_paths]


        print('Root:',self.root_fullpath)
        print('Stage ID:',self.stage_id_path)
        print('fullpath:',self.stage_id_fullpath)
        print('admin:', self.admin_path)
        print('admin_fullpath:', self.admin_fullpath)
        print('data:', self.data_path)
        print('data_fullpath:', self.data_fullpath)
        print('notes_path:',self.notes_path)
        print('notes_fullpath:',self.notes_fullpath)
        print('legal_path:',self.legal_path)
        print('legal_fullpath:',self.legal_fullpath)
        print('legal_paths:')
        for x in self.legal_paths:
            print('\t'+x)
        print('legal_fullpaths:')
        for x in self.legal_fullpaths:
            print('\t'+x)
        print('accession_records_path:',self.accession_records_path)
        print('accession_records_fullpath:',self.accession_records_fullpath)
        print('accession_record_paths:')
        for x in self.accession_record_paths:
            print('\t'+x)
        print('accession_record_fullpaths:')
        for x in self.accession_record_fullpaths:
            print('\t'+x)
