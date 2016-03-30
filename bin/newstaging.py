from collections import namedtuple
from uchicagoldr.fileprocessor import FileProcessor

if __name__ == "__main__":
    fp = FileProcessor("/media/repo/repository/tr/1cb381hv0gxsx",
                       "staging",
                       namedtuple("DirectoryInfo",
                                  "src_root dest_root directory_type directory_id prefix group_name resume")\
                       ("/media/repo/repository/tr","/home/tdanstrom/temporary",
                        "staging","foo","dir", "tdanstrom",2),
                       namedtuple("Rules", "numfiles")\
                       (32))
    fp.move()
    
