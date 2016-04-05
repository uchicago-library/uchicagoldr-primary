from os.path import join, split
from re import sub
from re import compile as re_compile

from filepathtree import FilePathTree
from rootedpath import RootedPath


class FileSuite(object):
    def __init__(self):
        self.original = None
        self.premis = []
        self.fits = []
        self.presforms = []

    def __repr__(self):
        selfdict = {}
        selfdict['original'] = self.original
        selfdict['premis'] = self.premis
        selfdict['fits'] = self.fits
        selfdict['presforms'] = self.presforms
        return str(selfdict)


class StageReader(object):

    re_trailing_numbers = re_compile('[0-9]+$')
    re_trailing_fits = re_compile('.fits.xml$')
    re_trailing_premis = re_compile('.premis.xml$')
    re_trailing_presform = re_compile('.presform(\.[\w]{3})?$')

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

        self.note_nodes = [self.fpt.tree.get_node(x) for x in
                           self.notes_node.fpointer]
        self.note_paths = [x.identifier for x in self.note_nodes]
        self.note_fullpaths = [join(self.root_fullpath, x) for x in
                               self.note_paths]

        self.legal_node = self.fpt.tree.get_node(join(self.admin_path, 'legal'))
        self.legal_path = self.legal_node.identifier
        self.legal_fullpath = join(self.root_fullpath, self.legal_path)

        self.legal_nodes = [self.fpt.tree.get_node(x) for x in
                            self.legal_node.fpointer]
        self.legal_paths = [x.identifier for x in self.legal_nodes]
        self.legal_fullpaths = [join(self.root_fullpath, x) for x in
                                self.legal_paths]

        self.accession_records_node = self.fpt.tree.get_node(
            join(self.admin_path, 'accession_records')
        )
        self.accession_records_path = self.accession_records_node.identifier
        self.accession_records_fullpath = join(self.root_fullpath,
                                               self.accession_records_path)

        self.accession_record_nodes = [self.fpt.tree.get_node(x) for x in
                                       self.accession_records_node.fpointer]
        self.accession_record_paths = [x.identifier for x in
                                       self.accession_record_nodes]
        self.accession_record_fullpaths = [join(self.root_fullpath, x)
                                           for x in self.accession_record_paths]

        self.data_prefix_nodes = [self.fpt.tree.get_node(x) for x in
                                  self.data_node.fpointer]
        self.data_prefix_paths = [x.identifier for x in
                                  self.data_prefix_nodes]
        self.data_prefix_fullpaths = [join(self.root_fullpath, x) for x in
                                      self.data_prefix_paths]

        self.admin_prefix_nodes = [self.fpt.tree.get_node(x) for x in
                                   self.admin_node.fpointer if
                                   (
                                       x != self.notes_node.identifier and
                                       x != self.legal_node.identifier and
                                       x != self.accession_records_node.identifier
                                   )
                                   ]
        self.admin_prefix_paths = [x.identifier for x in
                                   self.admin_prefix_nodes]
        self.admin_prefix_fullpaths = [join(self.root_fullpath, x) for x in
                                       self.admin_prefix_paths]

        self.prefix_nodes = self.data_prefix_nodes + self.admin_prefix_nodes
        self.prefix_paths = self.data_prefix_paths + self.admin_prefix_paths
        self.prefix_fullpaths = self.data_prefix_fullpaths + \
            self.admin_prefix_fullpaths

        self.prefixes = set([split(x)[1] for x in self.prefix_paths])
        self.prefix_root_strs = set(
            [sub(self.re_trailing_numbers, '', x) for x in self.prefixes]
        )

        self.manifest_nodes = self.get_manifest_node_from_prefix()
        self.manifest_paths = [x.identifier for x in self.manifest_nodes]
        self.manifest_fullpaths = [join(self.root_fullpath, x) for x in
                                   self.manifest_paths]

        self.premis_dir_nodes = self.get_premis_dir_node_from_prefix()
        self.premis_dir_paths = [x.identifier for x in self.premis_dir_nodes]
        self.premis_dir_fullpaths = [join(self.root_fullpath, x) for x in
                                     self.premis_dir_paths]

        self.premis_nodes = []
        for x in self.premis_dir_nodes:
            self.premis_nodes = self.premis_nodes + \
                self.fpt.tree.subtree(x.identifier).leaves()
        for x in self.premis_dir_nodes:
            if x in self.premis_nodes:
                del self.premis_nodes[self.premis_nodes.index(x)]
        self.premis_paths = [x.identifier for x in self.premis_nodes]
        self.premis_fullpaths = [join(self.root_fullpath, x) for x in
                                 self.premis_paths]

        self.data_nodes = [x for x in
                           self.fpt.tree.subtree(
                               self.data_node.identifier).all_nodes()]
        del self.data_nodes[self.data_nodes.index(self.data_node)]
        for x in self.data_prefix_nodes:
            del self.data_nodes[self.data_nodes.index(x)]
        self.data_paths = [x.identifier for x in self.data_nodes]
        self.data_fullpaths = [join(self.root_fullpath, x) for x in
                               self.data_paths]

        # I'm pretty sure a nor gate works here... but it is Monday
        # - past-Brian
        self.origin_data_nodes = [x for x in self.data_nodes if not (
            self.re_trailing_fits.search(x.identifier) or
            self.re_trailing_presform.search(x.identifier)
        )
        ]
        self.origin_data_paths = [x.identifier for x in self.origin_data_nodes]
        self.origin_data_fullpaths = [join(self.root_fullpath, x) for x in
                                      self.origin_data_paths]

        self.fits_data_nodes = [x for x in self.data_nodes if
                                self.re_trailing_fits.search(x.identifier)]
        self.fits_data_paths = [x.identifier for x in self.fits_data_nodes]
        self.fits_data_fullpaths = [join(self.root_fullpath, x) for x in
                                    self.fits_data_paths]

        self.converted_data_nodes = [x for x in self.data_nodes if
                                     self.re_trailing_presform.search(x.identifier)]
        self.converted_data_paths = [x.identifier for x in
                                     self.converted_data_nodes]
        self.converted_data_fullpaths = [join(self.root_fullpath, x) for x in
                                         self.converted_data_paths]

        self.prefix_pair_nodes = []
        for x in self.data_prefix_nodes:
            for y in self.admin_prefix_nodes:
                if split(x.identifier)[1] == split(y.identifier)[1]:
                    self.prefix_pair_nodes.append((x, y))
                    break
        self.prefix_pair_paths = [(x[0].identifier, x[1].identifier) for x in
                                  self.prefix_pair_nodes]
        self.prefix_pair_fullpaths = [(join(self.root_fullpath, x[0]),
                                       join(self.root_fullpath, x[1]))
                                      for x in self.prefix_pair_paths]

        self.file_suites_nodes = []
        for x in self.data_nodes:
            self.file_suites_nodes.append(self.build_file_suite_from_node(x))
        self.file_suites_paths = []
        for x in self.file_suites_nodes:
            pathfs = FileSuite()
            pathfs.original = x.original.identifier
            pathfs.premis = [y.identifier for y in x.premis]
            pathfs.fits = [y.identifier for y in x.fits]
            pathfs.presforms = [y.identifier for y in x.presforms]
            self.file_suites_paths.append(pathfs)
        self.file_suites_fullpaths = []
        for x in self.file_suites_paths:
            fullpathfs = FileSuite()
            fullpathfs.original = join(self.root_fullpath, x.original)
            fullpathfs.premis = [join(self.root_fullpath, y) for y in x.premis]
            fullpathfs.fits = [join(self.root_fullpath, y) for y in x.fits]
            fullpathfs.presforms = [join(self.root_fullpath, y) for y in x.presforms]
            self.file_suites_fullpaths.append(fullpathfs)

    def build_file_suite_from_node(self, n, recurse=False):
        fs = FileSuite()
        fs.original = n
        premis = self.get_premis_from_orig_node(n)
        if premis:
            fs.premis.append(premis)
        fits = self.get_fits_from_orig_node(n)
        if fits:
            fs.fits.append(fits)
        presforms = self.get_presform_from_orig_node(n)
        for x in presforms:
            if x:
                fs.presforms.append(x)
        if recurse is False:
            return fs
        for x in fs.premis:
            nextfs = self.build_file_suite_from_node(x, recurse=recurse)
            fs.premis = fs.premis + nextfs.premis
            fs.fits = fs.fits + nextfs.fits
            fs.presforms = fs.presforms + nextfs.presforms
        for x in fs.fits:
            nextfs = self.build_file_suite_from_node(x, recurse=recurse)
            fs.premis = fs.premis + nextfs.premis
            fs.fits = fs.fits + nextfs.fits
            fs.presforms = fs.presforms + nextfs.presforms
        for x in fs.presforms:
            nextfs = self.build_file_suite_from_node(x, recurse=recurse)
            fs.premis = fs.premis + nextfs.premis
            fs.fits = fs.fits + nextfs.fits
            fs.presforms = fs.presforms + nextfs.presforms
        return fs

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

    def get_manifest_path_from_prefix(self, prefix=None):
        return [x.identifier for x in
                self.get_manifest_node_from_prefix(prefix)]

    def get_premis_dir_node_from_prefix(self, prefix=None):
        ids = []
        for x in self.admin_prefix_nodes:
            if prefix is not None:
                if x.tag is not prefix:
                    continue
            for y in x.fpointer:
                if self.fpt.tree.get_node(y).tag == 'PREMIS':
                    ids.append(y)
        return [self.fpt.tree.get_node(x) for x in ids]

    def get_premis_dir_path_from_prefix(self, prefix=None):
        for x in self.prefix_nodes:
            if split(x.identifier)[1] == prefix:
                return join(x.identifier, 'PREMIS')

    def get_fits_from_orig_node(self, n):
        fits_id = self.hypothesize_fits_from_orig_node(n)
        node = self.fpt.tree.get_node(fits_id)
        if node:
            return node

    def hypothesize_fits_from_orig_node(self, n):
        fits_id = n.identifier + '.fits.xml'
        return fits_id

    def get_fits_from_orig_path(self, p):
        n = self.ftp.tree.get_node(p)
        return self.get_fits_from_orig_node(n).identifier

    def get_presform_from_orig_node(self, n):
        result = []
        orig_id = n.identifier
        presform_pattern = re_compile('^'+orig_id+'.presform(\.[\w]{3})?$')
        for n in self.fpt.tree.all_nodes():
            if presform_pattern.match(n.identifier):
                result.append(n)
        return result

    def get_presform_from_orig_path(self, p):
        n = self.ftp.tree.get_node(p)
        return self.get_presform_from_orig_node(n).identifier

    def get_premis_from_orig_node(self, n):
        premis_id = self.hypothesize_premis_from_orig_node(n)
        node = self.fpt.tree.get_node(premis_id)
        if node:
            return node

    def get_premis_from_orig_path(self, p):
        n = self.ftp.tree.get_node(p)
        return self.get_premis_from_orig_node(n).identifier

    def hypothesize_premis_from_orig_node(self, n):
        orig_id = n.identifier
        prefix = self.get_containing_prefix_string_from_path(orig_id)
        rel_path = RootedPath(orig_id, root=self.get_containing_prefix_dir_node_from_node(n).identifier)
        premis_id = join(self.admin_path, prefix, 'PREMIS',
                         rel_path.path + '.premis.xml')
        return premis_id

    def get_containing_prefix_dir_node_from_node(self, n):
        for x in self.fpt.trace_ancestry_of_a_node(n):
            if x in self.prefix_nodes:
                return x

    def get_containing_prefix_dir_path_from_path(self, p):
        n = self.fpt.tree.get_node(p)
        return self.get_containing_prefix_dir_node_from_node(n).identifier

    def get_containing_prefix_string_from_path(self, p):
        return split(self.get_containing_prefix_dir_path_from_path(p))[1]
