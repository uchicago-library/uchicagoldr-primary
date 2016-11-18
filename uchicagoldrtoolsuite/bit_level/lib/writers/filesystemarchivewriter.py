from json import dumps, dump
from os import makedirs
from os.path import exists, join, dirname, split
from tempfile import TemporaryDirectory
from uuid import uuid4
import xml.etree.ElementTree as ET
from logging import getLogger

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from pypairtree.utils import identifier_to_path
from pypairtree.pairtree import PairTree
from pypairtree.pairtreeobject import PairTreeObject
from pypairtree.intraobjectbytestream import IntraObjectByteStream

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
from uchicagoldrtoolsuite.core.lib.doi import DOI
from .abc.archiveserializationwriter import ArchiveSerializationWriter
from ..ldritems.ldrpath import LDRPath
from ..ldritems.ldritemcopier import LDRItemCopier
from ..ldritems.ldritemoperations import hash_ldritem


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company = "The University of Chicago Library"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class SegmentedPairTreeObject(PairTreeObject):
    """
    A quick wrapper for PairTreeObjects to store the segment id on them
    """

    _seg_id = None

    def get_seg_id(self):
        return self._seg_id

    def set_seg_id(self, x):
        self._seg_id = x

    seg_id = property(get_seg_id, set_seg_id)


class FileSystemArchiveWriter(ArchiveSerializationWriter):
    """
    Writes an archive structure to disk utilizing PairTrees as a series
    of directories and files.
    """
    @log_aware(log)
    def __init__(self, anArchive, aRoot, eq_detect="bytes"):
        """
        spawn a writer for the pairtree based Archive serialization

        __Args__

        1. anArchive (Archive): A populated archive structure
        2. aRoot (str): The path to a long term storage environment

        __KWArgs__

        * eq_detect (str): What equality detection metric to use while
            serializing
        """
        super().__init__(anArchive)
        self.lts_env_path = aRoot
        self.eq_detect = eq_detect
        log.debug("FileSystemArchiveWriter spawned: {}".format(str(self)))

    @log_aware(log)
    def __repr__(self):
        attr_dict = {
            'lts_env_path': self.lts_env_path,
            'eq_detect': self.eq_detect,
            'struct': str(self.get_struct())
        }
        return "<FileSystemArchiveWriter {}>".format(dumps(attr_dict,
                                                           sort_keys=True))

    @log_aware(log)
    def _write_ark_dir(self, clobber=False):
        ark_path = join(
            str(identifier_to_path(self.get_struct().identifier,
                                   root=self.lts_env_path)),
            "arf"
        )
        if exists(ark_path) and not clobber:
            err_text = "The Ark path ({}) ".format(ark_path) + \
                "already exists in the long term storage environment. " + \
                "Aborting."
            log.critical(err_text)
            raise OSError(err_text)
        else:
            makedirs(ark_path, exist_ok=True)
        self._write_file_acc_namaste_tag(ark_path)
        return ark_path

    @log_aware(log)
    def _write_dirs_skeleton(self, ark_path):
        admin_dir_path = join(ark_path, "admin")
        pairtree_root = join(ark_path, "pairtree_root")
        makedirs(pairtree_root, exist_ok=True)
        self._write_pairtree_namaste_tag(pairtree_root)
        accession_records_dir_path = join(admin_dir_path, "accession_records")
        adminnotes_dir_path = join(admin_dir_path, "adminnotes")
        legalnotes_dir_path = join(admin_dir_path, "legalnotes")

        for x in [admin_dir_path, pairtree_root, accession_records_dir_path,
                  adminnotes_dir_path, legalnotes_dir_path]:
            makedirs(x, exist_ok=True)
        return admin_dir_path, pairtree_root, accession_records_dir_path, \
            adminnotes_dir_path, legalnotes_dir_path

    @log_aware(log)
    def _put_materialsuite_into_pairtree(self, materialsuite,
                                         seg_id, pair_tree):
        obj_id = self._get_premis_obj_id(materialsuite.premis)
        o = SegmentedPairTreeObject(identifier=obj_id, encapsulation="arf")
        o.seg_id = seg_id
        content = IntraObjectByteStream(
            materialsuite.content,
            intraobjectaddress="content.file"
        )
        premis = IntraObjectByteStream(
            materialsuite.premis,
            intraobjectaddress="premis.xml"
        )
        if len(materialsuite.technicalmetadata_list) > 1:
            raise NotImplementedError(
                "The Archive serializer currently only supports " +
                "serializing a single FITs record as technical metadata."
            )
        fits = IntraObjectByteStream(
            materialsuite.technicalmetadata_list[0],
            intraobjectaddress="fits.xml"
        )
        o.add_bytestream(content)
        o.add_bytestream(premis)
        o.add_bytestream(fits)
        pair_tree.add_object(o)

    @log_aware(log)
    def _get_premis_obj_id(self, premis_ldritem):
        with TemporaryDirectory() as tmp_dir:
            premis_path = join(tmp_dir, uuid4().hex)
            tmp_item = LDRPath(premis_path)
            LDRItemCopier(premis_ldritem, tmp_item).copy()
            premis = PremisRecord(frompath=premis_path)
            return premis.get_object_list()[0].\
                get_objectIdentifier()[0].get_objectIdentifierValue()

    @log_aware(log)
    def _pack_archive_into_pairtree(self, pair_tree):
        for seg in self.get_struct().segment_list:
            seg_id = seg.identifier
            for materialsuite in seg.materialsuite_list:
                self._put_materialsuite_into_pairtree(materialsuite, seg_id,
                                                      pair_tree)

    @log_aware(log)
    def _write_data(self, pair_tree, ark_path, data_manifest):
        data_manifest['acc_id'] = self.get_struct().identifier
        data_manifest['objs'] = []
        for obj in pair_tree.objects:
            manifest_entry = {
                'identifier': obj.identifier,
                'origin_segment': obj.seg_id,
                'bytestreams': []
            }
            data_manifest['objs'].append(manifest_entry)
            for bytestream in obj.bytestreams:
                ms_path = join(ark_path,
                               pair_tree.root_dir_name,
                               str(identifier_to_path(obj.identifier)),
                               obj.encapsulation)
                makedirs(ms_path, exist_ok=True)
                self._write_materialsuite_namaste_tag(ms_path)
                path = join(ms_path,
                            bytestream.intraobjectaddress)
                makedirs(dirname(path), exist_ok=True)
                dst_item = LDRPath(path)
                cr = LDRItemCopier(bytestream.openable, dst_item).copy()
                manifest_dict = {
                    'origin': bytestream.openable.item_name,
                    'dst': dst_item.item_name,
                    'copy_report': cr
                }
                if not cr['src_eqs_dst']:
                    raise ValueError("{}".format(bytestream.openable.item_name))
                if bytestream.intraobjectaddress == "premis.xml":
                    self._update_premis_in_place(join(ms_path, "premis.xml"),
                                                 join(ms_path, "content.file"))
                    manifest_dict['type'] = "PREMIS"
                    manifest_dict['md5'] = hash_ldritem(dst_item, algo='md5')
                    manifest_dict['sha256'] = hash_ldritem(dst_item, algo='sha256')
                elif bytestream.intraobjectaddress == "fits.xml":
                    self._update_fits_in_place(join(ms_path, "fits.xml"),
                                               join(ms_path, "content.file"))
                    manifest_dict['type'] = "technical metadata"
                    manifest_dict['md5'] = hash_ldritem(dst_item, algo='md5')
                    manifest_dict['sha256'] = hash_ldritem(dst_item, algo='sha256')
                elif bytestream.intraobjectaddress == "content.file":
                    manifest_dict['type'] = "file content"
                    manifest_dict['md5'] = None
                    manifest_dict['sha256'] = None
                else:
                    raise ValueError("Unrecognized intraobject address!")
                manifest_entry['bytestreams'].append(manifest_dict)

    @log_aware(log)
    def _add_premis_acc_event(self, premis_rec):
        def _build_eventDetailInformation():
            return EventDetailInformation(eventDetail="bystream copied into " +
                                          "the long term storage environment.")

        def _build_eventIdentifier():
            return EventIdentifier("DOI", DOI().value)

        def _build_eventOutcomeInformation():
            return EventOutcomeInformation(eventOutcome="SUCCESS")

        def _build_event():
            e = Event(_build_eventIdentifier(), "ingestion", iso8601_dt())
            e.add_eventDetailInformation(_build_eventDetailInformation())
            e.add_eventOutcomeInformation(_build_eventOutcomeInformation())
            return e

        premis_rec.add_event(_build_event())

    @log_aware(log)
    def _update_premis_in_place(self, premis_path, obj_path):
        premis = PremisRecord(frompath=premis_path)
        premis.get_object_list()[0].\
            get_storage()[0].get_contentLocation().set_contentLocationValue(
                obj_path
            )
        self._add_premis_acc_event(premis)
        premis.write_to_file(premis_path)

    @log_aware(log)
    def _update_fits_in_place(self, fits_path, obj_path):
        ET.register_namespace('', "http://hul.harvard.edu/ois/xml/ns/fits/fits_output")
        ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
        tree = ET.parse(fits_path)
        root = tree.getroot()
        for x in root:
            if "fileinfo" in x.tag:
                for y in x:
                    if "filepath" in y.tag:
                        y.text = obj_path
                    if "filename" in y.tag:
                        y.text = split(obj_path)[1]
        tree.write(fits_path)

    @log_aware(log)
    def _write_data_manifest(self, data_manifest, admin_dir_path):
        with open(join(admin_dir_path, "data_manifest.json"), 'w') as f:
            dump(data_manifest, f, indent=4, sort_keys=True)

    @log_aware(log)
    def _write_file_acc_namaste_tag(self, dir_path):
        with open(join(dir_path, "0=icu-file-accession_0.1"), 'w') as f:
            f.write("icu-file-accession 0.1")

    @log_aware(log)
    def _write_pairtree_namaste_tag(self, dir_path):
        with open(join(dir_path, "0=pairtree_0.1"), 'w') as f:
            f.write("pairtree 0.1")

    @log_aware(log)
    def _write_materialsuite_namaste_tag(self, dir_path):
        with open(join(dir_path, "0=icu-materialsuite_0.1"), 'w') as f:
            f.write("icu-materialsuite 0.1")

    @log_aware(log)
    def _write_adminnotes(self, adminnotes_dir_path, admin_manifest):
        if self.get_struct().adminnote_list:
            for x in self.get_struct().adminnote_list:
                dst_path = join(adminnotes_dir_path, hash_ldritem(x, algo="crc32"))
                manifest_dict = {
                    'origin': x.item_name,
                    'acc_id': self.get_struct().identifier,
                    'type': 'admin note',
                    'dst': dst_path
                }
                dst_item = LDRPath(dst_path)
                cr = LDRItemCopier(x, dst_item).copy()
                if not cr['src_eqs_dst']:
                    raise ValueError("Bad admin note write!")
                manifest_dict['copy_report'] = cr
                manifest_dict['md5'] = hash_ldritem(dst_item, algo='md5')
                manifest_dict['sha256'] = hash_ldritem(dst_item, algo='sha256')
                admin_manifest.append(manifest_dict)

    @log_aware(log)
    def _write_legalnotes(self, legalnotes_dir_path, admin_manifest):
        if self.get_struct().legalnote_list:
            for x in self.get_struct().legalnote_list:
                dst_path = join(legalnotes_dir_path, hash_ldritem(x, algo="crc32"))
                manifest_dict = {
                    'origin': x.item_name,
                    'acc_id': self.get_struct().identifier,
                    'type': 'legal note',
                    'dst': dst_path
                }
                dst_item = LDRPath(dst_path)
                cr = LDRItemCopier(x, dst_item).copy()
                if not cr['src_eqs_dst']:
                    raise ValueError("Bad legal note write!")
                manifest_dict['copy_report'] = cr
                manifest_dict['md5'] = hash_ldritem(dst_item, algo='md5')
                manifest_dict['sha256'] = hash_ldritem(dst_item, algo='sha256')
                admin_manifest.append(manifest_dict)

    @log_aware(log)
    def _write_accessionrecords(self, accessionrecords_dir_path,
                                admin_manifest):
        for x in self.get_struct().accessionrecord_list:
            dst_path = join(accessionrecords_dir_path, hash_ldritem(x, algo="crc32"))
            manifest_dict = {
                'origin': x.item_name,
                'acc_id': self.get_struct().identifier,
                'type': 'accession_record',
                'dst': dst_path
            }
            dst_item = LDRPath(dst_path)
            cr = LDRItemCopier(x, dst_item).copy()
            if not cr['src_eqs_dst']:
                raise ValueError("Bad accession record write!")
            manifest_dict['copy_report'] = cr
            manifest_dict['md5'] = hash_ldritem(dst_item, algo='md5')
            manifest_dict['sha256'] = hash_ldritem(dst_item, algo='sha256')
            admin_manifest.append(manifest_dict)

    @log_aware(log)
    def _add_data_manifest_to_admin_manifest(self, admin_dir_path,
                                             admin_manifest):
        data_manifest_item = LDRPath(join(admin_dir_path, 'data_manifest.json'))
        manifest_dict = {
            'origin': None,
            'acc_id': self.get_struct().identifier,
            'type': 'data_manifest',
            'dst': 'data_manifest.json'
        }
        md5_hash_str = hash_ldritem(data_manifest_item, algo='md5')
        sha256_hash_str = hash_ldritem(data_manifest_item, algo='sha256')
        manifest_dict['md5'] = md5_hash_str
        manifest_dict['sha256'] = sha256_hash_str
        admin_manifest.append(manifest_dict)

    @log_aware(log)
    def _write_admin_manifest(self, admin_manifest, admin_dir_path):
        with open(join(admin_dir_path, 'admin_manifest.json'), 'w') as f:
            dump(admin_manifest, f, indent=4, sort_keys=True)

    @log_aware(log)
    def _write_WRITE_FINISHED(self, admin_dir_path):
        with open(join(admin_dir_path, "WRITE_FINISHED.json"), 'w') as f:
            dump(
                {"FINISHED_TIME": iso8601_dt(),
                 "FINISHED_STATUS": "GOOD"},
                f, indent=4, sort_keys=True
            )

    @log_aware(log)
    def write(self):
        """
        write the archive to disk at the specified location
        """
        log.debug("Writing Archive")

        ark_path = self._write_ark_dir()
        admin_dir_path, pairtree_root, accession_records_dir_path, \
            adminnotes_dir_path, legalnotes_dir_path = \
            self._write_dirs_skeleton(ark_path)

        data_manifest = {}
        admin_manifest = []

        pair_tree = PairTree(containing_dir=ark_path)
        self._pack_archive_into_pairtree(pair_tree)
        self._write_data(pair_tree, ark_path, data_manifest)
        self._write_data_manifest(data_manifest, admin_dir_path)
        self._write_adminnotes(adminnotes_dir_path, admin_manifest)
        self._write_legalnotes(legalnotes_dir_path, admin_manifest)
        self._write_accessionrecords(accession_records_dir_path, admin_manifest)
        self._add_data_manifest_to_admin_manifest(admin_dir_path, admin_manifest)
        self._write_admin_manifest(admin_manifest, admin_dir_path)
        self._write_WRITE_FINISHED(admin_dir_path)
