from datetime import datetime
from os import makedirs, mkdir
from os.path import exists, join, relpath, dirname
from .abc.serializationwriter import SerializationWriter
from ..convenience import copy
from .ldrpathregularfile import LDRPathRegularFile


class StagingDirectoryWriter(SerializationWriter):

    def __init__(self, aStructure):
        self.structure = aStructure

    def write(self, stage_directory, origin_root):
        print(stage_directory)
        print(origin_root)
        validated = self.structure.validate()
        if not validated:
            raise ValueError("Cannot serialize an invalid " +
                             " structure of type {}".
                             format(type(self.structure).__name__))
        else:
            if not exists(stage_directory):
                mkdir(stage_directory)
            if not exists(join(stage_directory, 'data')):
                mkdir(join(stage_directory, 'data'))
            if not exists(join(stage_directory, 'admin')):
                mkdir(join(stage_directory, 'admin'))
            for n_item in self.structure.segment:
                data_dir = join(stage_directory, 'data', n_item.identifier)
                admin_dir = join(stage_directory, 'admin', n_item.identifier)
                if not exists(data_dir):
                    mkdir(data_dir)
                if not exists(admin_dir):
                    mkdir(admin_dir)
                manifest = join(admin_dir, 'manifest.txt')
                manifest = LDRPathRegularFile(manifest)
                if not exists(manifest.item_name):
                    with manifest.open('wb') as mf:
                        today = datetime.today()

                        today_str = "manifest generated on {}".\
                                    format(str(today.year) + '-' +
                                           str(today.month) + '-' +
                                           str(today.day))
                        today_str = b"%s" % today_str
                        mf.write(today_str)
                    mf.close()

                for n_suite in n_item.materialsuite:
                    for req_part in n_suite.required_parts:
                        if type(getattr(n_suite, req_part, None)) == list:
                            for n_file in getattr(n_suite, req_part):
                                if stage_directory in n_file.item_name:
                                    pass
                                else:
                                    relevant_path = relpath(n_file.item_name,
                                                            origin_root)
                                    new_file_name = join(data_dir,
                                                         relevant_path)
                                    new_file = LDRPathRegularFile(
                                        new_file_name)
                                    print(dirname(new_file.item_name))
                                    makedirs(dirname(new_file.item_name),
                                             exist_ok=True)
                                    byte_data = None
                                    with n_file.open('rb') as reading_file:
                                        byte_data = reading_file.read()

                                    with new_file.open('wb') as writing_file:
                                        writing_file.write(byte_data)
                                    print(new_file)
                                # with n_file.open('rb') as origin_file:
                                #     print(origin_file.read())
                                # old_file = n_file
                                # relevant_path = relpath(n_file.item_name,
                                #                         origin_root)
                                # new_file_name = join(data_dir,
                                #                      relevant_path)
                                # new_file = LDRPathRegularFile(new_file_name)
                                # success, checksum1, checksum2 = copy(old_file,
                                #                                      new_file)
                                # with manifest.open('ab') as f:
                                #     f.write("{}\t{}\t{}\n".
                                #             format(relevant_path, checksum1,
                                #                    checksum2))-
