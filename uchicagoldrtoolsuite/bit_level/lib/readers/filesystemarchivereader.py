from os import scandir
from os.path import join, isdir, isfile, relpath
from json import load
from logging import getLogger

from pypremis.lib import PremisRecord

from pypairtree.pairtree import PairTree
from pypairtree.utils import identifier_to_path

from .abc.archiveserializationreader import ArchiveSerializationReader
from ..structures.segment import Segment
from ..structures.materialsuite import MaterialSuite
from ..ldritems.ldrpath import LDRPath


log = getLogger(__name__)


class FileSystemArchiveReader(ArchiveSerializationReader):
    """
    The reader for pairtree based FileSystem archive structure serializations

    Given the location of a long term storage environment and the identifier
    of an archive structure reconstructs the archive structure from byte
    streams serialized as files on disk.
    """
    def __init__(self, lts_path, identifier):
        """
        Create a new FileSystemArchiveReader

        __Args__

        1. lts_path (str): The file system path to the long term storage env
        2. identifier (str): The identifier of the archive structure stored
            in the given long term storage environment
        """
        super().__init__()
        self.lts_path = lts_path
        self.identifier = identifier

    def _read_skeleton(self, lts_path, identifier):
        arch_root = join(self.lts_path, str(identifier_to_path(identifier)),
                         "arf")
        pairtree_root = join(arch_root, "pairtree_root")
        admin_root = join(arch_root, "admin")
        if not isdir(arch_root):
            raise ValueError("No such identifier ({}) in the long term " +
                             "storage environment ({})!".format(
                                 self.lts_path, self.identifier))
        if not isdir(pairtree_root):
            raise ValueError("No pairtree root in Archive ({})!".format(
                self.identifier))
        if not isdir(admin_root):
            raise ValueError("No admin directory in Archive ({})!".format(
                self.identifier))

        admin_manifest_path = join(admin_root, "admin_manifest.json")
        data_manifest_path = join(admin_root, "data_manifest.json")
        accrec_dir_path = join(admin_root, "accession_records")
        adminnotes_path = join(admin_root, "adminnotes")
        legalnotes_path = join(admin_root, "legalnotes")

        if not isfile(admin_manifest_path):
            raise ValueError("No admin_manifest.json in Archive ({})!".format(
                self.identifier))
        if not isfile(data_manifest_path):
            raise ValueError("No data_manifest.json in Archive ({})!".format(
                self.identifier))
        if not isdir(accrec_dir_path):
            raise ValueError()
        if not isdir(adminnotes_path):
            raise ValueError()
        if not isdir(legalnotes_path):
            raise ValueError()

        return arch_root, pairtree_root, admin_root, admin_manifest_path, \
            data_manifest_path, accrec_dir_path, adminnotes_path, \
            legalnotes_path

    def _confirm_data_manifest_matches_filesystem(self, data_manifest,
                                                  identifier, pairtree):
        if not data_manifest['acc_id'] == identifier:
            raise ValueError("Identifier mismatch with data_manifest.json")

        ids_from_manifest = [x['identifier'] for x in data_manifest['objs']]
        num_ids_from_manifest = len(ids_from_manifest)
        i = 0
        for obj in pairtree.objects:
            if obj.identifier not in ids_from_manifest:
                raise ValueError("ID on filesystem that isn't in the " +
                                 "manifest: {}".format(obj.identifier))
            i += 1
        if i != num_ids_from_manifest:
            raise ValueError("ID(s) in the manifest that aren't on the " +
                             "file system!")

    def _read_data(self, data_manifest_path, identifier, pairtree):
        data_manifest = None
        with open(data_manifest_path, 'r') as f:
            data_manifest = load(f)

        self._confirm_data_manifest_matches_filesystem(data_manifest,
                                                       identifier,
                                                       pairtree)

        for ms_entry in data_manifest['objs']:
            # Create a segment if one doesn't exist with that identifier
            # otherwise grab the existing segment from the structure
            seg = None
            for x in self.get_struct().segment_list:
                if x.identifier == ms_entry['origin_segment']:
                    seg = x
            if seg is None:
                seg = Segment(
                    ms_entry['origin_segment'].split("-")[0],
                    int(ms_entry['origin_segment'].split("-")[1])
                )
                self.get_struct().add_segment(seg)
#            premis_path = None
#            for bytestream_entry in ms_entry['bytestreams']:
#                if bytestream_entry['type'] == "PREMIS":
#                    premis_path = bytestream_entry['dst']
#                    premis = PremisRecord(frompath=premis_path)
#                    try:
#                        relationships = premis.get_object_list()[0].\
#                            get_relationship()
#                    except KeyError:
#                        relationships = []
            seg.add_materialsuite(
                self._pack_materialsuite(ms_entry,
                                         data_manifest)
            )

    def _pack_materialsuite(self, ms_entry, data_manifest):
        ms = MaterialSuite()
        original_name = None
        premis = None
        for bytestream_entry in ms_entry['bytestreams']:
            if bytestream_entry['type'] == "file content":
                ms.content = LDRPath(bytestream_entry['dst'])
            if bytestream_entry['type'] == "technical metadata":
                ms.add_technicalmetadata(LDRPath(bytestream_entry['dst']))
            if bytestream_entry['type'] == "PREMIS":
                ms.premis = LDRPath(bytestream_entry['dst'])
                premis = PremisRecord(frompath=bytestream_entry['dst'])
                try:
                    original_name = premis.get_object_list()[0].get_originalName()
                except KeyError:
                    pass
                ms.identifier = premis.get_object_list()[0].get_objectIdentifier()[0].get_objectIdentifierValue()
        if original_name:
            ms.content.item_name = original_name
        return ms

    def _read_admin(self, admin_manifest_path, accrec_dir_path, adminnotes_path,
                    legalnotes_path, admin_root):
        # TODO: Add comparison with the manifest, probably, to mimic data
        # manifest behavior, even though this one uses the file system instead
        # of the manifest to find files.
#        admin_manifest = None
#        with open(admin_manifest_path, 'r') as f:
#            admin_manifest = load(f)
        for x in scandir(accrec_dir_path):
            accrec = LDRPath(x.path)
            accrec.item_name = relpath(x.path, accrec_dir_path)
            self.get_struct().add_accessionrecord(accrec)
        for x in scandir(adminnotes_path):
            adminnote = LDRPath(x.path)
            adminnote.item_name = relpath(x.path, adminnotes_path)
            self.get_struct().add_adminnote(adminnote)
        for x in scandir(legalnotes_path):
            legalnote = LDRPath(x.path)
            legalnote.item_name = relpath(x.path, legalnotes_path)
            self.get_struct().add_legalnote(legalnote)

    def read(self):
        """
        Reads the structure at the given location with the given identifier

        __Returns__

        self.struct (Archive): The archive structure
        """
        self.get_struct().identifier = self.identifier
        arch_root, pairtree_root, admin_root, admin_manifest_path, \
            data_manifest_path, accrec_dir_path, adminnotes_path, \
            legalnotes_path = self._read_skeleton()

        pairtree = PairTree(containing_dir=arch_root)
        pairtree.gather_objects()
        self._read_data(data_manifest_path, self.identifier, pairtree)

        self._read_admin(admin_manifest_path, accrec_dir_path, adminnotes_path,
                         legalnotes_path, admin_root)
        return self.get_struct()
