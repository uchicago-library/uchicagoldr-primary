from datetime import datetime
from os import makedirs, mkdir
from os.path import join, dirname, isdir

from .abc.stageserializationwriter import StageSerializationWriter
from .ldritemoperations import copy, hash_ldritem
from .ldrpath import LDRPath


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
        super().__init__(aStructure)
        self.stage_env_path = aRoot
        self.set_implementation('file system')

    def _write_ms_content(self, ms, data_dir):
        dst_path = join(data_dir, ms.get_content().item_name)
        self._make_containing_dir(dst_path)
        dst = LDRPath(dst_path, root=self.stage_env_path)
        cr = copy(ms.get_content(), dst, clobber=True)
        if cr.dst_hash is None:
            cr.dst_hash = hash_ldritem(dst)
        mf_line_str = "{}\t{}\n".format(dst.item_name, cr.dst_hash)
        mf_line_bytes = bytes(mf_line_str.encode('utf-8'))
        return mf_line_bytes

    def _write_ms_premis(self, ms, admin_dir):
        mf_line_bytes = bytes("", "utf-8")
        if ms.get_premis():
            dst_path = join(admin_dir, "PREMIS",
                            ms.get_content().item_name+".premis.xml")
            self._make_containing_dir(dst_path)
            dst = LDRPath(dst_path, root=self.stage_env_path)
            cr = copy(ms.get_premis(), dst, clobber=True)
            if cr.dst_hash is None:
                cr.dst_hash = hash_ldritem(dst)
            mf_line_str = "{}\t{}\n".format(dst.item_name, cr.dst_hash)
            mf_line_bytes = bytes(mf_line_str.encode('utf-8'))
        return mf_line_bytes

    def _write_ms_techmd(self, ms, admin_dir):
        mf_line_bytes = bytes("", "utf-8")
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
            mf_line_bytes = bytes(mf_line_str.encode('utf-8'))
        return mf_line_bytes

    def _write_ms_presforms(self, ms, data_dir, admin_dir):
        out = bytes("", "utf-8")
        if ms.get_presform_list():
            for x in ms.get_presform_list():
                out = out + self._write_ms_content(x, data_dir)
                out = out + self._write_ms_premis(x, admin_dir)
                out = out + self._write_ms_techmd(x, admin_dir)
                out = out + self._write_ms_presforms(x, data_dir, admin_dir)
        return out

    def _make_containing_dir(self, path):
        some_dir = dirname(path)
        makedirs(some_dir, exist_ok=True)

    def write(self):

        validated = self.get_struct().validate()
        if not validated:
            raise ValueError("Cannot serialize an invalid " +
                             " structure of type {}".
                             format(type(self.get_struct()).__name__))
        else:
            stage_directory = join(self.stage_env_path,
                                   self.get_struct().get_identifier())
            data_dir = join(stage_directory, 'data')
            admin_dir = join(stage_directory, 'admin')
            adminnotes_dir = join(admin_dir, 'adminnotes')
            accessionrecords_dir = join(admin_dir, 'accessionrecords')
            legalnotes_dir = join(admin_dir, 'legalnotes')

            for x in [stage_directory, data_dir, admin_dir, adminnotes_dir,
                      accessionrecords_dir, legalnotes_dir]:
                if not isdir(x):
                    mkdir(x)

            for n_item in self.get_struct().segment_list:
                cur_data_dir = join(data_dir, n_item.identifier)
                cur_admin_dir = join(admin_dir, n_item.identifier)
                if not isdir(cur_data_dir):
                    mkdir(cur_data_dir)
                if not isdir(cur_admin_dir):
                    mkdir(cur_admin_dir)
                manifest_path = join(cur_admin_dir, 'manifest.txt')
                manifest = LDRPath(manifest_path)
                if not manifest.exists():
                    with manifest.open('wb') as mf:
                        today = datetime.today()

                        today_str = "# manifest generated on {}\n".\
                                    format(str(today.year) + '-' +
                                           str(today.month) + '-' +
                                           str(today.day))
                        today_str = bytes(today_str.encode('utf-8'))
                        mf.write(today_str)

                for n_suite in n_item.materialsuite_list:
                    lines = []
                    lines.append(self._write_ms_content(n_suite, cur_data_dir))
                    lines.append(self._write_ms_premis(n_suite, cur_admin_dir))
                    lines.append(self._write_ms_techmd(n_suite, cur_admin_dir))
                    lines.append(self._write_ms_presforms(n_suite, cur_data_dir, cur_admin_dir))
                    with manifest.open('a') as mf:
                        for x in lines:
                            mf.write(x)
