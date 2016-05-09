from datetime import datetime
from os import makedirs, mkdir
from os.path import join, dirname, isdir, isfile
from sys import stderr, stdout

from .abc.stageserializationwriter import StageSerializationWriter
from .ldritemoperations import copy
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

    def write(self, clobber=False):

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
                    for orig in n_suite.get_original_list():
                        recv_item_path = join(cur_data_dir,
                                              orig.item_name)
                        if isfile(recv_item_path) and not clobber:
                            continue
                        if not isdir(dirname(recv_item_path)):
                            makedirs(dirname(recv_item_path), exist_ok=True)
                        recv_item = LDRPath(join(cur_data_dir, orig.item_name))
                        success, checksum_matched, copy_status, checksum1 = \
                            copy(orig, recv_item, clobber=clobber)
                        # do stderr printing here
                        with manifest.open('a') as mf:
                            mf_line_str = "{}\t{}\n".format(orig.item_name,
                                                            checksum1)
                            mf_line_bytes = bytes(mf_line_str.encode('utf-8'))
                            mf.write(mf_line_bytes)
                    for premis in n_suite.get_premis_list():
                        recv_item_path = join(cur_admin_dir,
                                              "PREMIS",
                                              orig.item_name)
                        if isfile(recv_item_path) and not clobber:
                            continue
                        if not isdir(dirname(recv_item_path)):
                            makedirs(dirname(recv_item_path), exist_ok=True)
                        recv_item = LDRPath(join(cur_admin_dir, "PREMIS",
                                                 orig.item_name))
                        success, checksum_matched, copy_status, checksum1 = \
                            copy(orig, recv_item, clobber=clobber)
                        # do stderr printing here
                        with manifest.open('a') as mf:
                            mf_line_str = "{}\t{}\n".format(orig.item_name,
                                                            checksum1)
                            mf_line_bytes = bytes(mf_line_str.encode('utf-8'))
                            mf.write(mf_line_bytes)
                    for presform in n_suite.get_presform_list():
                        recv_item_path = join(cur_data_dir,
                                              orig.item_name)
                        if isfile(recv_item_path) and not clobber:
                            continue
                        if not isdir(dirname(recv_item_path)):
                            makedirs(dirname(recv_item_path), exist_ok=True)
                        recv_item = LDRPath(join(cur_data_dir, orig.item_name))
                        success, checksum_matched, copy_status, checksum1 = \
                            copy(orig, recv_item, clobber=clobber)
                        # do stderr printing here
                        with manifest.open('a') as mf:
                            mf_line_str = "{}\t{}\n".format(orig.item_name,
                                                            checksum1)
                            mf_line_bytes = bytes(mf_line_str.encode('utf-8'))
                            mf.write(mf_line_bytes)
                    for techmd in n_suite.get_technicalmetadata_list():
                        recv_item_path = join(cur_admin_dir, "TECHMD",
                                              orig.item_name)
                        if isfile(recv_item_path) and not clobber:
                            continue
                        if not isdir(dirname(recv_item_path)):
                            makedirs(dirname(recv_item_path), exist_ok=True)
                        recv_item = LDRPath(join(cur_data_dir, orig.item_name))
                        success, checksum_matched, copy_status, checksum1 = \
                            copy(orig, recv_item, clobber=clobber)
                        # do stderr printing here
                        with manifest.open('a') as mf:
                            mf_line_str = "{}\t{}\n".format(orig.item_name,
                                                            checksum1)
                            mf_line_bytes = bytes(mf_line_str.encode('utf-8'))
                            mf.write(mf_line_bytes)
