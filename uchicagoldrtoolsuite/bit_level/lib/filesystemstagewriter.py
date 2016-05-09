from datetime import datetime
from os import makedirs, mkdir
from os.path import exists, join, relpath, dirname
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
    def __init__(self, aStructure):
        super().__init__(aStructure)
        self.set_implementation('file system')

    def write(self, stage_directory, origin_root):

        validated = self.get_struct().validate()
        if not validated:
            raise ValueError("Cannot serialize an invalid " +
                             " structure of type {}".
                             format(type(self.get_struct()).__name__))
        else:
            data_dir = join(stage_directory, 'data')
            admin_dir = join(stage_directory, 'admin')
            if not exists(stage_directory):
                mkdir(stage_directory)
            if not exists(admin_dir):
                mkdir(admin_dir)
            if not exists(data_dir):
                mkdir(data_dir)
            adminnotes_dir = join(admin_dir, 'adminnotes')
            accessionrecords_dir = join(admin_dir, 'accessionrecords')
            legalnotes_dir = join(admin_dir, 'legalnotes')
            if not exists(data_dir):
                mkdir(data_dir)
            if not exists(admin_dir):
                mkdir(admin_dir)
            if not exists(data_dir):
                mkdir(data_dir)
            if not exists(admin_dir):
                mkdir(admin_dir)
            if not exists(adminnotes_dir):
                mkdir(adminnotes_dir)
            if not exists(accessionrecords_dir):
                mkdir(accessionrecords_dir)
            if not exists(legalnotes_dir):
                mkdir(legalnotes_dir)
            for n_item in self.get_struct().segment_list:
                cur_data_dir = join(data_dir, n_item.identifier)
                cur_admin_dir = join(admin_dir, n_item.identifier)
                if not exists(cur_data_dir):
                    mkdir(cur_data_dir)
                if not exists(cur_admin_dir):
                    mkdir(cur_admin_dir)
                manifest = join(cur_admin_dir, 'manifest.txt')
                manifest = LDRPath(manifest)
                if not exists(manifest.item_name):
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
                        pass
                    for premis in n_suite.get_premis_list():
                        pass
                    for presform in n_suite.get_presform_list():
                        pass
                    for techmd in n_suite.get_technicalmetadata_list():
                        pass
#                    for req_part in n_suite.required_parts:
#                        if type(getattr(n_suite, req_part, None)) == list:
#                            for n_file in getattr(n_suite, req_part):
#                                if stage_directory in n_file.item_name:
#                                    pass
#                                else:
#                                    relevant_path = relpath(n_file.item_name,
#                                                            origin_root)
#                                    new_file_name = join(cur_data_dir,
#                                                         relevant_path)
#                                    new_file = LDRPath(
#                                        new_file_name)
#                                    makedirs(dirname(new_file.item_name),
#                                             exist_ok=True)
#                                    success = False
#                                    success, checksum_matched, copy_status,\
#                                        checksum1 = copy(n_file,
#                                                         new_file)
#                                    if not success:
#                                        stderr.write("{} could not ".
#                                                     format(n_file.item_name +
#                                                            "be copied to {}".
#                                                            format(
#                                                                new_file.
#                                                                item_name)))
#                                    if copy_status == 'copied':
#                                        if checksum_matched:
#                                            manifest_line = "{}\t{}\n".\
#                                                            format(relevant_path,
#                                                                   checksum1)
#                                            manifest_line = bytes(
#                                                manifest_line.encode('utf-8'))
#                                            with manifest.open('ab') as f:
#                                                f.write(manifest_line)
#                                        elif copy_status == 'already moved':
#                                            stderr.write("no checksum for {}\n".
#                                                         format(new_file.
#                                                                item_name))
#                                    else:
#                                        stdout.write("{} was "
#                                                     .format(relevant_path) +
#                                                     " already present" +
#                                                     " in the segment\n")
