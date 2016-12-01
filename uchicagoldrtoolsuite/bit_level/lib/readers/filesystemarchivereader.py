from os import scandir
from os.path import join, isdir, isfile, relpath
from json import load
from logging import getLogger

from pypremis.lib import PremisRecord

from pypairtree.pairtree import PairTree
from pypairtree.utils import identifier_to_path

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from .abc.archiveserializationreader import ArchiveSerializationReader
from ..structures.segment import Segment
from ..structures.materialsuite import MaterialSuite
from ..ldritems.ldrpath import LDRPath


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class FileSystemArchiveReader(ArchiveSerializationReader):
    """
    The reader for pairtree based FileSystem archive structure serializations

    Given the location of a long term storage environment and the identifier
    of an archive structure reconstructs the archive structure from byte
    streams serialized as files on disk.
    """
    @log_aware(log)
    def __init__(self, lts_path, identifier):
        """
        Create a new FileSystemArchiveReader

        __Args__

        1. lts_path (str): The file system path to the long term storage env
        2. identifier (str): The identifier of the archive structure stored
            in the given long term storage environment
        """
        log_init_attempt(self, log, locals())
        super().__init__()
        self.lts_path = lts_path
        self.identifier = identifier
        log_init_success(self, log)

    @log_aware(log)
    def _read_skeleton(self, lts_path, identifier):
        log.info("Reading the essential subdirs of the Archive serialization")
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
            raise ValueError("No accession record subdir")
        if not isdir(adminnotes_path):
            raise ValueError("No adminnotes subdir")
        if not isdir(legalnotes_path):
            raise ValueError("No legalnotes subdir")

        log.info("Archive skeleton read/located")
        return arch_root, pairtree_root, admin_root, admin_manifest_path, \
            data_manifest_path, accrec_dir_path, adminnotes_path, \
            legalnotes_path

    @log_aware(log)
    def _confirm_data_manifest_matches_filesystem(self, data_manifest,
                                                  identifier, pairtree):
        log.debug("Comparing the file system to the manifest")
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
                             "file system! or vice versa")
        log.debug("Comparison of the file system to the manifest complete")

    @log_aware(log)
    def _read_data(self, data_manifest_path, identifier, pairtree):
        log.info("Reading archive data")
        data_manifest = None
        with open(data_manifest_path, 'r') as f:
            data_manifest = load(f)

        self._confirm_data_manifest_matches_filesystem(data_manifest,
                                                       identifier,
                                                       pairtree)

        log.debug("Packaging objects...")
        for ms_entry in data_manifest['objs']:
            # Create a segment if one doesn't exist with that identifier
            # otherwise grab the existing segment from the structure
            log.debug("Packaging object")
            seg = None
            log.debug("Determining object segment")
            for x in self.get_struct().segment_list:
                if x.identifier == ms_entry['origin_segment']:
                    seg = x
                    log.debug("Segment already exists on Archive")
            if seg is None:
                log.debug("Segment does not exist on Archive, creating")
                seg = Segment(
                    ms_entry['origin_segment'].split("-")[0],
                    int(ms_entry['origin_segment'].split("-")[1])
                )
                log.debug(
                    "Adding Segment({}) to Archive".format(seg.identifier)
                )
                self.get_struct().add_segment(seg)
            log.debug("Delegating to MaterialSuite packager and adding " +
                      "result to the segment")
            seg.add_materialsuite(
                self._pack_materialsuite(ms_entry,
                                         data_manifest)
            )
            log.debug("Object packaging complete")
        log.debug("Finished packaging objects")

    @log_aware(log)
    def _pack_materialsuite(self, ms_entry, data_manifest):
        log.debug("Packaging a MaterialSuite from disk")
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
        log.debug("MaterialSuite packaged")
        return ms

    @log_aware(log)
    def _read_admin(self, admin_manifest_path, accrec_dir_path, adminnotes_path,
                    legalnotes_path, admin_root):
        # TODO: Add comparison with the manifest, probably, to mimic data
        # manifest behavior, even though this one uses the file system instead
        # of the manifest to find files.
        log.info("Reading the administrative data from disk")
        log.debug("Reading accession records")
        for x in scandir(accrec_dir_path):
            accrec = LDRPath(x.path)
            accrec.item_name = relpath(x.path, accrec_dir_path)
            self.get_struct().add_accessionrecord(accrec)
        log.debug("Reading adminnotes")
        for x in scandir(adminnotes_path):
            adminnote = LDRPath(x.path)
            adminnote.item_name = relpath(x.path, adminnotes_path)
            self.get_struct().add_adminnote(adminnote)
        log.debug("Reading legalnotes")
        for x in scandir(legalnotes_path):
            legalnote = LDRPath(x.path)
            legalnote.item_name = relpath(x.path, legalnotes_path)
            self.get_struct().add_legalnote(legalnote)

    @log_aware(log)
    def read(self):
        """
        Reads the structure at the given location with the given identifier

        __Returns__

        self.struct (Archive): The archive structure
        """
        log.info("Reading Archive from disk serialization")
        self.get_struct().identifier = self.identifier
        arch_root, pairtree_root, admin_root, admin_manifest_path, \
            data_manifest_path, accrec_dir_path, adminnotes_path, \
            legalnotes_path = self._read_skeleton()

        pairtree = PairTree(containing_dir=arch_root)
        pairtree.gather_objects()
        self._read_data(data_manifest_path, self.identifier, pairtree)

        self._read_admin(admin_manifest_path, accrec_dir_path, adminnotes_path,
                         legalnotes_path, admin_root)
        log.debug("Read complete")
        return self.get_struct()
