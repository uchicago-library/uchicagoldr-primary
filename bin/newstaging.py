from uchicagoldr import FileProcessor

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--resume","-r",type=int, action='store')
    parser.add_argument("directory", type=str, action='store')
    parser.add_argument("source_root", type=str, action='store')
    parser.add_argument("destination_root", type=str, action='store')
    parser.add_argument("staging_id", type=str, action='store')
    parser.add_argument("prefix", type=str, action='store')
    parser.parse_args()

    fp = FileProcessor(args.directory,
                       namedtuple("DirectoryInfo",
                                  "src_root dest_root directory_type directory_id prefix")\
                       (),
                       )
    fp.move()

    
    # fp = FileProcessor("/media/repo/repository/tr/buffer/lloyd",
    #                    namedtuple("DirectoryInfo", "src_root dest_root kind staging_id prefix")\
    #                    ("/media/repo/repository/tr/buffer","/home/tdanstrom/temporary",
    #                     "stager","foo","dir")
    #                    namedtuple("Rules")\
    #                    (
    #     fp.move()
