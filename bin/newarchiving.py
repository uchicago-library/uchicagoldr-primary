
from argparse import ArgumentParser
from collection import namedtuple
from uchicagoldr.fileporocessor import FileProcessor

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("directory", type=str, action'store')
    parser.add_argument("source_root", type=str, action='store')
    parser.add_argument("destination_root", type=int, action='store')
    parser.add_argument("numfiles", type=int, action='store')
    parser.add_argument("numfolders", type=int, action='store')
    args = parser.parse_args()
    fp = FileProcessor(args.directory, 'archiving', namedtuple("DirectoryInfo",
                                                  "src_root dest_root directory_id prefix " +\
                                                  "directory_type resume group_name validation")
                       (args.source_root, args.destination_root, args.staging_id,
                        args.prefix, 'archiving', args.resume,
                        args.group,
                        {'numfiles':args.numfiles, 'numfolders':args.numfolders}))
    fp.move()
