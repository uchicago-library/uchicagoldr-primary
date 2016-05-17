from os import makedirs
from os.path import join, dirname, isfile

from .abc.stageserializationwriter import StageSerializationWriter
from .ldritemoperations import copy, hash_ldritem
from .ldrpath import LDRPath
from ...core.lib.convenience import iso8601_dt


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FileSystemStageWriter(StageSerializationWriter):
    """
    writes a Staging Structure to disk as a series of directories and files
    """
    def __init__(self, aStructure, aRoot):
        """
        spawn a writer

        __Args__

        1. aStructure (Stage): The Stage to write to disk
        2. aRoot (str): The path to your staging environment
        """
        super().__init__(aStructure)
        self.stage_env_path = aRoot
        self.set_implementation('file system')

    def _make_containing_dir(self, path):
        some_dir = dirname(path)
        makedirs(some_dir, exist_ok=True)

    def _make_dir(self, dir_path):
        makedirs(dir_path, exist_ok=True)

    def _write_seg(self, seg, data_path, admin_path):
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

        with open(manifest_path, 'a') as f:
            for ms in seg.materialsuite_list:
                self._write_materialsuite(
                    ms,
                    seg_data_path,
                    seg_admin_path,
                    f
                )

    def _write_materialsuite(self, ms, seg_data_path, seg_admin_path,
                             manifest_flo):
        self._write_ms_content(ms, seg_data_path, manifest_flo)
        self._write_ms_premis(ms, seg_admin_path, manifest_flo)
        self._write_ms_techmd(ms, seg_admin_path, manifest_flo)
        self._write_ms_presforms(ms, seg_data_path, seg_admin_path,
                                 manifest_flo)

    def _write_ms_content(self, ms, data_dir, manifest_flo):
        dst_path = join(data_dir, ms.get_content().item_name)
        self._make_containing_dir(dst_path)
        dst = LDRPath(dst_path, root=self.stage_env_path)
        cr = copy(ms.get_content(), dst, clobber=True)
        if cr.dst_hash is None:
            cr.dst_hash = hash_ldritem(dst)
        mf_line_str = "{}\t{}\n".format(dst.item_name, cr.dst_hash)
        manifest_flo.write(mf_line_str)

    def _write_ms_premis(self, ms, admin_dir, manifest_flo):
        if ms.get_premis():
            dst_path = join(admin_dir, "PREMIS",
                            ms.get_content().item_name+".premis.xml")
            self._make_containing_dir(dst_path)
            dst = LDRPath(dst_path, root=self.stage_env_path)
            cr = copy(ms.get_premis(), dst, clobber=True)
            if cr.dst_hash is None:
                cr.dst_hash = hash_ldritem(dst)
            mf_line_str = "{}\t{}\n".format(dst.item_name, cr.dst_hash)
            manifest_flo.write(mf_line_str)

    def _write_ms_techmd(self, ms, admin_dir, manifest_flo):
        if ms.get_technicalmetadata_list():
            if len(ms.get_technicalmetadata_list()) > 1:
                raise NotImplementedError("Currently the serializer only " +
                                          "handles a single FITS record in " +
                                          "the techmd array.")
            dst_path = join(admin_dir, "TECHMD",
                            ms.get_content().item_name+".fits.xml")
            self._make_containing_dir(dst_path)
            dst = LDRPath(dst_path, root=self.stage_env_path)
            cr = copy(ms.get_technicalmetadata(0), dst, clobber=True)
            if cr.dst_hash is None:
                cr.dst_hash = hash_ldritem(dst)
            mf_line_str = "{}\t{}\n".format(dst.item_name, cr.dst_hash)
            manifest_flo.write(mf_line_str)

    def _write_ms_presforms(self, ms, data_dir, admin_dir, manifest_flo):
        if ms.get_presform_list():
            for x in ms.get_presform_list():
                x.content.item_name = ms.content.item_name+".presform"+x.extension
                self._write_ms_content(x, data_dir, manifest_flo)
                self._write_ms_premis(x, admin_dir, manifest_flo)
                self._write_ms_techmd(x, admin_dir, manifest_flo)
                self._write_ms_presforms(x, data_dir, admin_dir, manifest_flo)

    def write(self):

        validated = self.get_struct().validate()
        if not validated:
            raise ValueError("Cannot serialize an invalid " +
                             " structure of type {}".
                             format(type(self.get_struct()).__name__))

        stage_directory = join(self.stage_env_path,
                               self.get_struct().get_identifier())

        self._make_dir(stage_directory)

        data_dir = join(stage_directory, 'data')
        admin_dir = join(stage_directory, 'admin')
        adminnotes_dir = join(admin_dir, 'adminnotes')
        accessionrecords_dir = join(admin_dir, 'accessionrecords')
        legalnotes_dir = join(admin_dir, 'legalnotes')

        for x in [stage_directory, data_dir, admin_dir, adminnotes_dir,
                  accessionrecords_dir, legalnotes_dir]:
            self._make_dir(x)

        for seg in self.get_struct().segment_list:
            self._write_seg(seg, data_dir, admin_dir)

        for legalnote in self.get_struct().get_legalnote_list():
            recv_item_path = join(legalnotes_dir, legalnote.item_name)
            recv_item = LDRPath(recv_item_path, root=legalnotes_dir)
            copy(legalnote, recv_item)

        for adminnote in self.get_struct().get_adminnote_list():
            recv_item_path = join(adminnotes_dir, adminnote.item_name)
            recv_item = LDRPath(recv_item_path, root=adminnotes_dir)
            copy(adminnote, recv_item)

        for accessionrecord in self.get_struct().get_accessionrecord_list():
            recv_item_path = join(accessionrecords_dir, accessionrecord.item_name)
            recv_item = LDRPath(recv_item_path, root=accessionrecords_dir)
            copy(accessionrecord, recv_item)
