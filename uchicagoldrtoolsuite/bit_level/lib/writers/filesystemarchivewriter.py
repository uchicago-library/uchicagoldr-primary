from json import dumps, dump
from os import makedirs
from os.path import exists, join
from logging import getLogger

from pypairtree.utils import identifier_to_path
from pypremis.nodes import Event, EventDetailInformation, EventIdentifier

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from uchicagoldrtoolsuite.core.lib.doi import DOI
from .filesystemmaterialsuitewriter import FileSystemMaterialSuiteWriter
from ..ldritems.ldrpath import LDRPath
from ..ldritems.ldritemcopier import LDRItemCopier
from ..ldritems.ldritemoperations import hash_ldritem
from .abc.archiveserializationwriter import ArchiveSerializationWriter


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company = "The University of Chicago Library"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class FileSystemArchiveWriter(ArchiveSerializationWriter):
    """
    Writes an archive structure to disk utilizing PairTrees as a series
    of directories and files.
    """
    @log_aware(log)
    def __init__(self, anArchive, aRoot, eq_detect="bytes",
                 materialsuite_serializer=FileSystemMaterialSuiteWriter):
        """
        spawn a writer for the pairtree based Archive serialization

        __Args__

        1. anArchive (Archive): A populated archive structure
        2. aRoot (str): The path to a long term storage environment

        __KWArgs__

        * eq_detect (str): What equality detection metric to use while
            serializing
        """
        log_init_attempt(self, log, locals())
        super().__init__(anArchive, aRoot, materialsuite_serializer,
                         eq_detect=eq_detect)
        self.set_implementation("filesystem (pairtree)")
        log_init_success(self, log)

    @log_aware(log)
    def _write_ark_dir(self, clobber=False):
        log.info("Writing ARK directory")
        ark_path = join(
            str(identifier_to_path(self.get_struct().identifier,
                                   root=self.root)),
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
    def _write_file_acc_namaste_tag(self, dir_path):
        with open(join(dir_path, "0=icu-file-accession_0.1"), 'w') as f:
            f.write("icu-file-accession 0.1")

    @log_aware(log)
    def _write_dirs_skeleton(self, ark_path):
        log.info("Writing required subdirs for an Archive serialization.")
        admin_dir_path = join(ark_path, "admin")
        pairtree_root = join(ark_path, "pairtree_root")
        makedirs(pairtree_root, exist_ok=True)
        self._write_pairtree_namaste_tag(pairtree_root)
        accession_records_dir_path = join(admin_dir_path, "accession_records")
        adminnotes_dir_path = join(admin_dir_path, "adminnotes")
        legalnotes_dir_path = join(admin_dir_path, "legalnotes")

        for x in [admin_dir_path, pairtree_root, accession_records_dir_path,
                  adminnotes_dir_path, legalnotes_dir_path]:
            log.debug("Creating dir at {}".format(x))
            makedirs(x, exist_ok=True)
        return admin_dir_path, pairtree_root, accession_records_dir_path, \
            adminnotes_dir_path, legalnotes_dir_path

    @log_aware(log)
    def _write_data(self, pairtree_root):

        def _build_eventDetailInformation():
            return EventDetailInformation(eventDetail="bystream copied into " +
                                          "the long term storage environment.")

        def _build_event():
            e = Event(_build_eventIdentifier(), "ingestion", iso8601_dt())
            e.add_eventDetailInformation(_build_eventDetailInformation())
            return e

        def _build_eventIdentifier():
            return EventIdentifier("DOI", DOI().value)

        log.info("Writing archive data")
        for x in self.struct.materialsuite_list:
            ms_writer = self.materialsuite_serializer(
                x, pairtree_root, encapsulation="arf",
                update_content_location=True, premis_event=_build_event(),
                clobber=False
            )
            ms_writer.write()
        log.info("Archive data written")

    @log_aware(log)
    def _write_pairtree_namaste_tag(self, dir_path):
        with open(join(dir_path, "0=pairtree_0.1"), 'w') as f:
            f.write("pairtree 0.1")

    @log_aware(log)
    def _write_adminnotes(self, adminnotes_dir_path, admin_manifest):
        log.info("Writing adminnotes")
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
        log.info("Writing legalnotes")
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
        log.info("Writing accession records")
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
    def _write_admin_manifest(self, admin_manifest, admin_dir_path):
        log.debug("Writing admin manifest")
        with open(join(admin_dir_path, 'admin_manifest.json'), 'w') as f:
            dump(admin_manifest, f, indent=4, sort_keys=True)

    @log_aware(log)
    def _write_WRITE_FINISHED(self, admin_dir_path):
        log.debug("Writing archive cap")
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
        log.info("Writing Archive")

        ark_path = self._write_ark_dir()
        admin_dir_path, pairtree_root, accession_records_dir_path, \
            adminnotes_dir_path, legalnotes_dir_path = \
            self._write_dirs_skeleton(ark_path)

        admin_manifest = []

        self._write_data(pairtree_root)
        self._write_adminnotes(adminnotes_dir_path, admin_manifest)
        self._write_legalnotes(legalnotes_dir_path, admin_manifest)
        self._write_accessionrecords(accession_records_dir_path, admin_manifest)
        self._write_admin_manifest(admin_manifest, admin_dir_path)
        self._write_WRITE_FINISHED(admin_dir_path)
        log.info("Archive written")

    @log_aware(log)
    def set_root(self, x):
        if not isinstance(x, str):
            raise TypeError(
                "{} is a {}, not a str!".format(
                    str(x), str(type(x))
                )
            )
        self._root = x
