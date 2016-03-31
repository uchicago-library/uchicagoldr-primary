from argparse import ArgumentParser
from uchicagoldr.fileprocessor import FileProcessor

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--resume","-r", help="An integer for a run that needs to be resumed.",
                        type=int, action='store')
    parser.add_argument("directory", help="The directory that needs to be staged.",
                        type=str, action='store')
    parser.add_argument("source_root", help="The root of the directory that needs to be staged.",
                        type=str, action='store')
    parser.add_argument("destination_root", type=str, action='store')
    parser.add_argument("staging_id", type=str, action='store')
    parser.add_argument("prefix", type=str, action='store')
    parser.parse_args()

    # fp = FileProcessor(args.directory,
    #                    namedtuple("DirectoryInfo",
    #                               "src_root dest_root directory_type directory_id prefix")\
    #                    (args.source_root, args.destination_root, 'staging', args.staging_id,
    #                     args.prefix),
    #                    )
    # fp.move()

    
    # fp = FileProcessor("/media/repo/repository/tr/buffer/lloyd",
    #                    namedtuple("DirectoryInfo", "src_root dest_root kind staging_id prefix")\
    #                    ("/media/repo/repository/tr/buffer","/home/tdanstrom/temporary",
    #                     "stager","foo","dir")
    #                    namedtuple("Rules")\
    #                    (
    #     fp.move()
