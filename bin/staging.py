
from argparse import Action, ArgumentParser
from os import _exit
from uchicagoldr.tree import Stager

__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__copyright__ = "2016"
__publication__ = "2016-02-08"
__version__ = "1.0.0"

class ValidateDirectory(Action):
    def __call__(self, parser, namespace, values, option_string = None):
        if not exists(value):
            raise IOError("{} does not exist on the filesystem")
        setattr(args, self.dest, value)

def main():
    parser = ArgumentParser(description="run this command to stage a directory of material and move it into the ldr",epilog="Copyright {company} {date}; written by <{email}>.".format(company = __copyright__, date = __publication__, email = __email__))
    parser.add_argument("directory",
                        help="Enter a valid directory that needs to be staged",
                        action=ValidateDirectory)
    parser.add_argument("arkid",help="Enter the ldr identifier",
                        action="store",type=str)
    parser.add_argument("eadnum",help="Enter the spcl ead identifier",
                        action="store",type=str)
    parser.add_argument("accnum",help="Enter the spcl accession identifer",
                        action="store",type=str)
    parser.add_argument("prefix",
                        help="Enter the prefix used for the folders in data and admin",
                        action="store",type=str)
    parser.add_argument("numfiles",
                        help="Enter the total number of files in the directory",
                        action="store",type=int)
    parser.add_argument("numfolders",
                        help="Enter the number of prefix enumerated folders that are present in admin and data",
                        action="store",type=int)
    parser.add_argument("source_root")
    parser.add_argument("destination_root")
    args = parser.parse_args()
    
    try:
        s = Stager(args.directory, args.eadnum, args.arkid, args.accnum, args.prefix, args.numfolders, args.numfiles, args.source_root, args.destination_root)
        is_it_valid = s.validate()
        if is_it_valid():
            # since it's valid, time to do the actual ingest
            #s.ingest()
            pass
        else:
            # get an explanation of the validation errors
            s.explain_validation_results()
            
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
