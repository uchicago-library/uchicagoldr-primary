from os import makedirs
from os.path import join, dirname, isfile
from json import dumps

from .abc.stageserializationwriter import StageSerializationWriter
from ..ldritems.ldritemoperations import hash_ldritem
from ..ldritems.ldritemcopier import LDRItemCopier
from ..ldritems.ldrpath import LDRPath
from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from uchicagoldrtoolsuite.core.lib.exceptionhandler import ExceptionHandler


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"

log = spawn_logger(__name__)
eh = ExceptionHandler()


class FileSystemStageWriter(StageSerializationWriter):
    """
    writes a Staging Structure to disk as a series of directories and files
    """
    def __init__(self, aStructure, aRoot, eq_detect="bytes"):
        """
        spawn a writer

        __Args__

        1. aStructure (Stage): The Stage to write to disk
        2. aRoot (str): The path to your staging environment

        __KWArgs__

        * eq_detect (str): The equality detection metric to pass to
            LDRItemCopier when writing
        """
        super().__init__(aStructure)
        self.stage_env_path = aRoot
        self.set_implementation('file system')
        self.eq_detect = eq_detect
        log.debug("FileSystemStageWriter spawned: {}".format(str(self)))

    def __repr__(self):
        attrib_dict = {
            'stage_env_path': self.stage_env_path,
            'eq_detect': self.eq_detect,
            'struct': str(self.get_struct())
        }
        return "<FileSystemStageWriter {}>".format(dumps(attrib_dict, sort_keys=True))

    def _make_containing_dir(self, path):
        some_dir = dirname(path)
        makedirs(some_dir, exist_ok=True)

    def _make_dir(self, dir_path):
        makedirs(dir_path, exist_ok=True)

    def _write_seg(self, seg, data_path, admin_path):
        try:
            seg_data_path = join(data_path, seg.identifier)
            seg_admin_path = join(admin_path, seg.identifier)

            self._make_dir(seg_data_path)
            self._make_dir(seg_admin_path)

            manifest_path = join(seg_admin_path, 'manifest.txt')
            if isfile(manifest_path):
                with open(manifest_path, 'a') as f:
                    f.write('# manifest appended to at {}\n'.format(iso8601_dt()))
            else:
                with open(manifest_path, 'w') as f:
                    f.write('# manifest created at {}\n'.format(iso8601_dt()))

        except Exception as e:
            eh.handle(e, raise_exceptions=True)

        with open(manifest_path, 'a') as f:
            ms_num = 0
            for ms in seg.materialsuite_list:
                ms_num += 1
                log.debug(
                    "Writing MaterialSuite {}/{}".format(
                    str(ms_num),
                    str(len(seg.materialsuite_list))
                    )
                )
                self._write_materialsuite(
                    ms,
                    seg_data_path,
                    seg_admin_path,
                    f
                )

    def _write_materialsuite(self, ms, seg_data_path, seg_admin_path,
                             manifest_flo):
        try:
            self._write_ms_content(ms, seg_data_path, manifest_flo)
            self._write_ms_premis(ms, seg_admin_path, manifest_flo)
            self._write_ms_techmd(ms, seg_admin_path, manifest_flo)
            self._write_ms_presforms(ms, seg_data_path, seg_admin_path,
                                    manifest_flo)
        except Exception as e:
            eh.handle(e)

    def _write_ms_content(self, ms, data_dir, manifest_flo):
        try:
            dst_path = join(data_dir, ms.get_content().item_name)
            self._make_containing_dir(dst_path)
            dst = LDRPath(dst_path, root=data_dir)
            c = LDRItemCopier(ms.get_content(), dst, clobber=True, eq_detect=self.eq_detect)
            r = c.copy()
            manifest_flo.write(self._interpret_copy_report(r, dst))
        except Exception as e:
            eh.handle(e)

    def _write_ms_premis(self, ms, admin_dir, manifest_flo):
        try:
            if ms.get_premis():
                dst_path = join(admin_dir, "PREMIS",
                                ms.get_content().item_name+".premis.xml")
                self._make_containing_dir(dst_path)
                dst = LDRPath(dst_path, root=join(admin_dir, "PREMIS"))
                c = LDRItemCopier(ms.get_premis(), dst, clobber=True, eq_detect=self.eq_detect)
                r = c.copy()
                manifest_flo.write(self._interpret_copy_report(r, dst))
        except Exception as e:
            eh.handle(e)

    def _write_ms_techmd(self, ms, admin_dir, manifest_flo):
        try:
            if ms.get_technicalmetadata_list():
                if len(ms.get_technicalmetadata_list()) > 1:
                    raise NotImplementedError("Currently the serializer only " +
                                            "handles a single FITS record in " +
                                            "the techmd array.")
                dst_path = join(admin_dir, "TECHMD",
                                ms.get_content().item_name+".fits.xml")
                self._make_containing_dir(dst_path)
                dst = LDRPath(dst_path, root=join(admin_dir, "TECHMD"))
                c = LDRItemCopier(ms.get_technicalmetadata(0), dst, clobber=True, eq_detect=self.eq_detect)
                r = c.copy()
                manifest_flo.write(self._interpret_copy_report(r, dst))
        except Exception as e:
            eh.handle(e)

    def _write_ms_presforms(self, ms, data_dir, admin_dir, manifest_flo):
        try:
            if ms.get_presform_list():
                for x in ms.get_presform_list():
                    print(x.extension)
                    x.content.item_name = ms.content.item_name + \
                        ".presform" + \
                        x.extension
                    self._write_ms_content(x, data_dir, manifest_flo)
                    self._write_ms_premis(x, admin_dir, manifest_flo)
                    self._write_ms_techmd(x, admin_dir, manifest_flo)
                    self._write_ms_presforms(x, data_dir, admin_dir, manifest_flo)
        except Exception as e:
            eh.handle(e)

    def _interpret_copy_report(self, cr, dst):
        if cr['copied']:
            h = hash_ldritem(dst)
            cr['sha256'] = h
        if not cr['copied']:
            cr['sha256'] = None
        return dst.item_name+"\t"+dumps(cr)+"\n"


    def write(self):

        log.debug("Writing Stage")

        try:
            validated = self.get_struct().validate()
            if not validated:
                raise ValueError("Cannot serialize an invalid " +
                                " structure of type {}".
                                format(type(self.get_struct()).__name__))
        except Exception as e:
            eh.handle(e, raise_exceptions=True)

        stage_directory = join(self.stage_env_path,
                               self.get_struct().get_identifier())

        log.debug("Writing Staging Directory")
        log.debug("Staging Directory Location: {}".format(stage_directory))
        try:
            self._make_dir(stage_directory)
        except Exception as e:
            eh.handle(e, raise_exceptions=True)

        data_dir = join(stage_directory, 'data')
        admin_dir = join(stage_directory, 'admin')
        adminnotes_dir = join(admin_dir, 'adminnotes')
        accessionrecords_dir = join(admin_dir, 'accessionrecords')
        legalnotes_dir = join(admin_dir, 'legalnotes')

        try:
            log.debug("Writing Staging Directory skeleton")
            for x in [stage_directory, data_dir, admin_dir, adminnotes_dir,
                    accessionrecords_dir, legalnotes_dir]:
                self._make_dir(x)
        except Exception as e:
            eh.handle(e, raise_exceptions=True)

        try:
            seg_num = 0
            for seg in self.get_struct().segment_list:
                seg_num += 1
                log.debug("Writing segment {}/{}".format(str(seg_num), str(len(self.get_struct().segment_list))))
                self._write_seg(seg, data_dir, admin_dir)
        except Exception as e:
            eh.handle(e)

        try:
            legalnote_num = 0
            for legalnote in self.get_struct().get_legalnote_list():
                legalnote_num += 1
                log.debug("Writing legalnote {}/{}".format(str(legalnote_num), str(len(self.get_struct().get_legalnote_list()))))
                recv_item_path = join(legalnotes_dir, legalnote.item_name)
                recv_item = LDRPath(recv_item_path, root=legalnotes_dir)
                c = LDRItemCopier(legalnote, recv_item, eq_detect=self.eq_detect)
                c.copy()
        except Exception as e:
            eh.handle(e)

        try:
            adminnote_num = 0
            for adminnote in self.get_struct().get_adminnote_list():
                adminnote_num += 1
                log.debug("Writing adminnote {}/{}".format(str(adminnote_num), str(len(self.get_struct().get_adminnote_list()))))
                recv_item_path = join(adminnotes_dir, adminnote.item_name)
                recv_item = LDRPath(recv_item_path, root=adminnotes_dir)
                c = LDRItemCopier(adminnote, recv_item, eq_detect=self.eq_detect)
                c.copy()
        except Exception as e:
            eh.handle(e)

        try:
            accessionrecord_num = 0
            for accessionrecord in self.get_struct().get_accessionrecord_list():
                accessionrecord_num += 1
                log.debug("Writing accessionrecord {}/{}".format(str(accessionrecord_num), str(len(self.get_struct().get_accessionrecord_list()))))
                recv_item_path = join(accessionrecords_dir,
                                    accessionrecord.item_name)
                recv_item = LDRPath(recv_item_path, root=accessionrecords_dir)
                c = LDRItemCopier(accessionrecord, recv_item, eq_detect=self.eq_detect)
                c.copy()
        except Exception as e:
            eh.handle(e)
