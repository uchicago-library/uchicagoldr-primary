from argparse import ArgumentParser
from uchicagoldr.fileprocessor import FileProcessor

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--resume","-r", help="An integer for a run that needs to be resumed.",
                        type=int, action='store', default=False)
    parser.add_argument("--group", "-g", help="The name of a group to assign group ownership to the new staging directory",
                        type=str, action='store', default='None')
    parser.add_argument("directory", help="The directory that needs to be staged.",
                        type=str, action='store')
    parser.add_argument("source_root", help="The root of the directory that needs to be staged.",
                        type=str, action='store')
    parser.add_argument("destination_root", help="The location that the staging diectory should be created",
                        type=str, action='store')
    parser.add_argument("staging_id", help="The identifying name for the new staging directory",
                        type=str, action='store')
    parser.add_argument("prefix", help="The prefix defining the type of run that is being processed",
                        type=str, action='store')
    parser.parse_args()

    fp = FileProcessor(args.directory, namedtuple("DirectoryInfo",
                                                  "src_root dest_root directory_id" +\
                                                  "prefix directory_type group_name " +\
                                                  "resume group_name")\
                       (args.source_root, args.destination_root, args.staging_id,
                        args.prefix, 'staging', args.resume, args.group))
    print(fp)
