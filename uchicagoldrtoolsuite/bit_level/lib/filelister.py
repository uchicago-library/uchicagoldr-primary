"""The FileLister class is what FileProcessor delegates getting the right files to
"""

from os import listdir
from os.path import exists, join
from .absolutefilepathtree import AbsoluteFilePathTree


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
        directory_root = getattr(info, 'dest_root', None)
        directory_id = getattr(info, 'directory_id', None)
        if not exists(join(directory_root, directory_id)):
            return self.data
        else:
            directory_type = getattr(info, 'directory_type', None)
            directory = join(directory_root, directory_id)
            if directory_type == 'staging':
                self.data = self.staging_resume_filter(directory, info.prefix, info.resume)
                return self.data
            else:
                raise ValueError("invalid directory type")


    def staging_resume_filter(self, directory: str, prefix: str, resume: int):
        """A method for reading a staging directory for purposes of resuming a
        partially completed staging run.
        """
        if resume == 0:
            return self.data
        else:
            previous_runs = [join(directory, 'data', x)
                             for x in listdir(join(directory, 'data'))]
            if len(previous_runs) == 0:
                raise ValueError("Cannot find anything in in the directory specified")
            else:
                dir_to_care_about = prefix+str(resume)
                resume_dir = [x for x in previous_runs
                              if x.endswith(dir_to_care_about)]
                if len(resume_dir) == 0:
                    raise ValueError("Could not find the resumption token {}".format(resume) +\
                                     " that you specified")
                else:
                    tree = AbsoluteFilePathTree(join(directory, 'data',
                                                     resume_dir[-1]))
                    split_string = join(directory, 'data', str(prefix+str(resume)))
                    finished_files = [x.split(split_string)[1] for x in tree.get_files()]
                    done = []
                    for a_file in self.data:
                        for a_potential_match in finished_files:
                            if a_potential_match in a_file:
                                done.append(a_file)
                                break
                            newdata = [x for x in self.data if x not in done]
                    return newdata

