from os.path import join, split
from re import sub
from re import compile as re_compile

from uchicagoldr.filepathtree import FilePathTree
from uchicagoldr.rootedpath import RootedPath


class StageReader(object):

    re_trailing_numbers = re_compile('[0-9]+$')
    re_trailing_fits = re_compile('.fits.xml$')
    re_trailing_premis = re_compile('.premis.xml$')

    def __init__(self, rootedpath):
        if not isinstance(rootedpath, RootedPath):
            raise ValueError()

        self.fpt = FilePathTree(rootedpath, leaf_dirs=True)

        self.root_node = self.fpt.tree.root
        self.root_fullpath = rootedpath.root

        self.stage_id_path = rootedpath.path
        self.stage_id_node = self.fpt.find_tag_at_depth(self.stage_id_path, 1)
        self.stage_id_fullpath = rootedpath.fullpath

        self.admin_node = self.fpt.tree.get_node(join(self.stage_id_path,
                                                      'admin'))
        self.admin_path = self.admin_node.identifier
        self.admin_fullpath = join(self.root_fullpath, self.admin_path)

        self.data_node = self.fpt.tree.get_node(join(self.stage_id_path,
                                                     'data'))
        self.data_path = self.data_node.identifier
        self.data_fullpath = join(self.root_fullpath, self.data_path)

        self.notes_node = self.fpt.tree.get_node(join(self.admin_path,
                                                      'notes'))
        self.notes_path = self.notes_node.identifier
        self.notes_fullpath = join(self.root_fullpath, self.notes_path)

        self.note_nodes = (self.fpt.tree.get_node(x) for x in
                           self.notes_node.fpointer)
        self.note_paths = (x.identifier for x in self.note_nodes)
        self.note_fullpaths = (join(self.root_fullpath, x) for x in
                               self.note_paths)

        self.legal_node = self.fpt.tree.get_node(join(self.admin_path, 'legal'))
        self.legal_path = self.legal_node.identifier
        self.legal_fullpath = join(self.root_fullpath, self.legal_path)

        self.legal_nodes = (self.fpt.tree.get_node(x) for x in
                            self.legal_node.fpointer)
        self.legal_paths = (x.identifier for x in self.legal_nodes)
        self.legal_fullpaths = (join(self.root_fullpath, x) for x in
                                self.legal_paths)

        self.accession_records_node = self.fpt.tree.get_node(
            join(self.admin_path, 'accession_records')
        )
        self.accession_records_path = self.accession_records_node.identifier
        self.accession_records_fullpath = join(self.root_fullpath,
                                               self.accession_records_path)

        self.accession_record_nodes = (self.fpt.tree.get_node(x) for x in
                                       self.accession_records_node.fpointer)
        self.accession_record_paths = (x.identifier for x in
                                       self.accession_record_nodes)
        self.accession_record_fullpaths = (join(self.root_fullpath, x)
                                           for x in self.accession_record_paths)

        self.data_prefix_nodes = (self.fpt.tree.get_node(x) for x in
                                  self.data_node.fpointer)
        self.data_prefix_paths = (x.identifier for x in
                                  self.data_prefix_nodes)
        self.data_prefix_fullpaths = (join(self.root_fullpath, x) for x in
                                      self.data_prefix_paths)

        self.admin_prefix_nodes = (self.fpt.tree.get_node(x) for x in
                                   self.admin_node.fpointer if
                                   (
                                       x != self.notes_node.identifier and
                                       x != self.legal_node.identifier and
                                       x != self.accession_records_node.identifier
                                   )
                                   )
        self.admin_prefix_paths = (x.identifier for x in
                                   self.admin_prefix_nodes)
        self.admin_prefix_fullpaths = (join(self.root_fullpath, x) for x in
                                       self.admin_prefix_paths)

        self.prefix_nodes = self.data_prefix_nodes + self.admin_prefix_nodes
        self.prefix_paths = self.data_prefix_paths + self.admin_prefix_paths
        self.prefix_fullpaths = self.data_prefix_fullpaths + \
            self.admin_prefix_fullpaths

        self.prefixes = set((split(x)[1] for x in self.prefix_paths))
        self.prefix_root_strs = set(
            (sub(self.re_trailing_numbers, '', x) for x in self.prefixes)
        )

        self.manifest_nodes = self.get_manifest_node_from_prefix()
        self.manifest_paths = (x.identifier for x in self.manifest_nodes)
        self.manifest_fullpaths = (join(self.root_fullpath, x) for x in
                                   self.manifest_paths)

        self.premis_dir_nodes = self.get_premis_dir_node_from_prefix()
        self.premis_dir_paths = (x.identifier for x in self.premis_dir_nodes)
        self.premis_dir_fullpaths = (join(self.root_fullpath, x) for x in
                                     self.premis_dir_paths)

        self.premis_nodes = (self.fpt.tree.subtree(x).leaves() for x in
                             self.premis_dir_nodes)
        self.premis_paths = (x.identifier for x in self.premis_nodes)
        self.premis_fullpaths = (join(self.root_fullpath, x) for x in
                                 self.premis_paths)

        self.data_nodes = (x for x in
                           self.fpt.tree.subtree(self.data_node).all_nodes())
        self.data_paths = (x.identifier for x in self.data_nodes)
        self.data_fullpaths = (join(self.root_fullpath, x) for x in
                               self.data_paths)

        # I'm pretty sure a nor gate works here... but it is Monday
        # - past-Brian
        self.origin_data_nodes = (x for x in self.data_nodes if not (
            FilePathPatterns.fits_filepath.match(x.identifier) or
            FilePathPatterns.presform_filepath.match(x.identifier)
        )
        )
        self.origin_data_paths = (x.identifier for x in self.origin_data_nodes)
        self.origin_data_fullpaths = (join(self.root_fullpath, x) for x in
                                      self.origin_data_paths)

        self.fits_data_nodes = (x for x in self.data_nodes if
                                FilePathPatterns.fits_filepath.match(x.identifier))
        self.fits_data_paths = (x.identifier for x in self.fits_data_nodes)
        self.fits_data_fullpaths = (join(self.root_fullpath, x) for x in
                                    self.fits_data_paths)

        self.converted_data_nodes = None
        self.converted_data_paths = None
        self.converted_data_fullpaths = None

        self.prefix_pair_nodes = None
        self.prefix_pair_paths = None
        self.prefix_pair_fullpaths = None

        self.file_suites_nodes = None
        self.file_suites_paths = None
        self.file_suites_fullpaths = None

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
        print('data_prefix_paths:')
        for x in self.data_prefix_paths:
            print('\t'+x)
        print('data_prefix_fullpaths:')
        for x in self.data_prefix_fullpaths:
            print('\t'+x)
        print('admin_prefix_paths:')
        for x in self.admin_prefix_paths:
            print('\t'+x)
        print('prefixes:')
        for x in self.prefixes:
            print('\t'+x)

    def get_manifest_node_from_prefix(self, prefix=None):
        ids = []
        for x in self.admin_prefix_nodes:
            if prefix is not None:
                if x.tag is not prefix:
                    continue
            for y in x.fpointer:
                if self.fpt.tree.get_node(y).tag == 'manifest.txt':
                    ids.append(y)
        return (self.fpt.tree.get_node(x) for x in ids)

    def get_premis_node_from_prefix(self, prefix=None):
        ids = []
        for x in self.admin_prefix_nodes:
            if prefix is not None:
                if x.tag is not prefix:
                    continue
            for y in x.fpointer:
                if self.gpt.tree.get_node(y).tag == 'PREMIS':
                    ids.append(y)
        return (self.fpt.tree.get_node(x) for x in ids)
