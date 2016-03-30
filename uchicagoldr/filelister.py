"""The FileLister class is what FileProcessor delegates getting the right files to
"""

from os import listdir
from os.path import join
from uchicagoldr.absolutefilepathtree import AbsoluteFilePathTree


class FileLister(object):
    """The FileLister class is in charge of filtering out the relevant files
    for a given project.
    """
    def __init__(self, file_list: list):
        if len(file_list) == 0:
            raise ValueError("Cannot pass an empty list to FileLister")
        self.data = file_list

    def filter_files(self, info) -> list:
        """A method for evluating the type of directory being managed and modify the
        data attribute with the correct file list.
        """
        directory_root = getattr(info, 'destination_root', None)
        directory_id = getattr(info, 'directory_id', None)
        directory_type = getattr(info, 'directory_type', None)
        directory = join(directory_root, directory_id)
        if directory_type == 'staging':
            self.data = self.staging_resume_filter(directory, info.prefix, info.resume)
        else:
            raise ValueError("invalid directory type")


    def staging_resume_filter(self, directory: str, prefix: str, resume: int):
        """A method for reading a staging directory for purposes of resuming a
        partially completed staging run.
        """
        previous_runs = [join(directory, 'data', x)
                         for x in listdir(directory)]
        if len(previous_runs) == 0:
            raise ValueError("Cannot find anything in in the directory specified")
        else:
            dir_to_care_about = prefix+str(resume)
            resume_dir = [x for x in previous_runs
                          if x.endswith(dir_to_care_about)]
            if len(resume_dir) == 0:
                raise ValueError("Could not find the resumption token you specified")
            else:
                tree = AbsoluteFilePathTree(join(directory, 'data', resume_dir[-1]))
                finished_files = tree.get_files()
                unfinished_files = [x for x in self.data if x not in finished_files]
                self.data = unfinished_files
