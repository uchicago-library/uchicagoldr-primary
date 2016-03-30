
from typing import NamedTuple
from uchicagoldr.absolutefilepathtree import AbsoluteFilePathTree


class FileLister(object):
    def __init__(self, file_list: list):
        if len(file_list) == 0:
            raise ValueError("Cannot pass an empty list to FileLister")
        self.data = file_list

    def filter_files, info: NamedTuple("DirectoryInfo", [])) -> list:
        if resume_token:
            resumption = getattr(info, 'resume', None)
            directory_root = getattr(info, 'destination_root', None)
            directory_id = getattr(info, 'directory_id', None)
            directory_type = getattr(info, 'directory_type', None)
            directory = join(directory_root, directory_id)
            if directory_type == 'staging':
                directory = join(directory_root, 'data')
                previous_runs = [join(directory_root, 'data', x)
                                 for x in listdir(directory)]
            if len(previous_runs) == 0:
                raise ValueError("Cannot find anything in in the directory specified")
            else:
                resume_dir = [x for x in in previous_runs if x.endswith(info.prefix+str(info.resume))]
                if len(resume_dir) == 0:
                    raise ValueError("Could not find the resumption token you specified")
                else:
                    tree = AbsoluteFilePathTree(join(directory, 'data', resume_dir[-1]))
                    finished_files = tree.get_files()
                    unfinished_files = [for x in self.data if x not in finished_files]
                    self.data = unfinished_files
        else:
            return self.files
                
