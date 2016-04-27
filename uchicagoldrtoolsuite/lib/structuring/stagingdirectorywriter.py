from datetime import datetime
from os import mkdir
from os.path import exists, join, relpath
from .abc.serializationwriter import SerializationWriter
from .ldrpathregulardirectory import LDRPathRegularDirectory
from .ldrpathregularfile import LDRPathRegularFile


class StagingDirectoryWriter(SerializationWriter):

    def __init__(self, aStructure):
        self.structure = aStructure

    def write(self, stage_directory, origin_root):
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
                    mf = open(manifest, 'ab')
                    today = datetime.today()
                    mf.write("# manifest generated on {}".
                             format(datetime.now().isoformat(today.year +
                                                             '-' + today.month +
                                                             '-' + today.day)))
                    mf.close()

                for n_suite in n_item.materialsuite:
                    for req_part in n_suite.required_parts:
                        if type(getattr(n_suite, req_part, None)) == list:
                            for n_file in getattr(n_suite, req_part):
                                old_file = n_file
                                relevant_path = relpath(n_file.item_name,
                                                        origin_root)
                                new_file_name = join(data_dir.item_name,
                                                     relevant_path)
                                new_file = LDRPathRegularFile(new_file_name)
                                success, checksum1, checksum2 = copy(old_file,
                                                                     new_file)
                                with manifest.open('ab') as f:
                                    f.write("{}\t{}\t{}\n".
                                            format(relevant_path, checksum1,
                                                   checksum2))
