
from argparse import Action, ArgumentParser
from os import _exit
from os.path import exists, join, relpath
from sys import stderr, stdout
from uchicagoldr.tree import Stager

__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "University of Chicago"
__copyright__ = "University of Chicago, 2016"
__publication__ = "2016-02-08"
__version__ = "1.0.0"

class ValidateDirectory(Action):
    def __call__(self, parser, namespace, value, option_string = None):
        if not exists(value):
            print(value)
            raise IOError("{} does not exist on the filesystem")
        setattr(namespace, self.dest, value)

def main():
    parser = ArgumentParser(description="run this command to stage a directory of material and move it into the ldr",epilog="Copyright {copyright}; written by <{email}>.".format(copyright = __copyright__, email = __email__))
    parser.add_argument("-r","--resume",help="Set this if you want to resume a semi-complete run",action="store_true")
    parser.add_argument("directory",
                        help="Enter a valid directory that needs to be staged",
                        action=ValidateDirectory)
    parser.add_argument("numfiles",
                        help="Enter the total number of files in the directory",
                        action="store",type=int)
    parser.add_argument("stage_id",
                        help="Enter the name  for the top of the new staging directory.",
                        action="store",type=str)
    parser.add_argument("prefix",
                        help="Enter the prefix for the subdirectories.",
                        action="store",type=str)    
    parser.add_argument("source_root",help="Enter the root of the source directory")
    parser.add_argument("destination_root",help="Enter the root fo the destination directory")
    args = parser.parse_args()
    print(args.resume)
    try:
        s = Stager(args.directory, args.numfiles, args.stage_id, args.prefix, args.source_root, args.destination_root)
        is_it_valid = s.validate()
        if is_it_valid:
            s.ingest(resume_partially_completed_run = args.resume)
            destination_directory = join(args.destination_root,
                                         relpath(args.directory, args.source_root))
            stdout.write("{} has been moved into {}\n".format(args.directory, destination_directory))
        else:
            problem = s.explain_validation_result()
            stderr.write("{}: {}\n".format(problem.category, problem.message))
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
