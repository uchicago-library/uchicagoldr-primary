
from argparse import Action, ArgumentParser
from os import _exit
from os.path import exists, join, relpath
from sys import stderr, stdout
from uchicagoldr.tree import Pruner

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
    parser = ArgumentParser(description="run this command to prune unnecessary " + \
                            "files from a staged directory",
                            epilog="Copyright {copyright}; written by <{email}>." \
                            .format(copyright = __copyright__, email = __email__))
    parser.add_argument("directory",
                        help="Enter a valid directory that needs to be staged",
                        action=ValidateDirectory)
    parser.add_argument("source_root",
                        help="Enter the root of the directory",
                        action=ValidateDirectory)
    parser.add_argument("patterns",
                        help="Enter a list of regular expressions matching " + \
                        "file names that can be deleted from the staging directory",
                        action='store',nargs="*")
    args = parser.parse_args()
    print(args)
    try:
        p = Pruner(args.directory, args.source_root, args.patterns)
        is_it_valid = p.validate()
        if is_it_valid:

            numfiles_deleted = p.ingest()
            stdout.write("{} have been removed from {}\n".format(str(num_files_deleted), args.directory))
        else:
            problem = p.explain_validation_result()
            stderr.write("{}: {}\n".format(problem.category, problem.message))
    # try:
    #     s = Stager(args.directory, args.numfiles, args.stage_id,
    #                args.prefix, args.source_root, args.destination_root)
    #     is_it_valid = s.validate()
    #     if is_it_valid:
    #         s.ingest(resume_partially_completed_run = args.resume)
    #         destination_directory = join(args.destination_root,
    #                                      relpath(args.directory, args.source_root))
    #         stdout.write("{} has been moved into {}\n".format(args.directory, destination_directory))
    #     else:
    #         problem = s.explain_validation_result()
    #         stderr.write("{}: {}\n".format(problem.category, problem.message))
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
