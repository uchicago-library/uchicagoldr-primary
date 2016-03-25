import argparse
from os.path import isdir, split, join
from os import makedirs
from uchicagoldr.premisobjectrecordcreator import PremisObjectRecordCreator
from uchicagoldr.rootedpath import RootedPath
from uchicagoldr.stagereader import StageReader


def write_records(records):
    while records:
        x = records.pop()
        target_path = x[1]
        record = x[0]
        if not isdir(split(target_path)[0]):
            makedirs(split(target_path)[0])
        record.write_to_file(target_path)


def build_record(path):
    return PremisObjectRecordCreator(path).get_record()


def build_stage_reader(path, root):
    rooted_path = RootedPath(path, root=root)
    stage_reader = StageReader(rooted_path)
    return stage_reader


def main():
    # Parser instantiation
    parser = argparse.ArgumentParser(description='Generate original minimal' +
                                     'PREMIS object records for files in a' +
                                     'uchicagoldr staging structure.')

    parser.add_argument(
        'path',
        help='Specify the path to the staging id'
    )

    parser.add_argument(
        '-r', '--root',
        default=None,
        help='Specify the root path for the staging directory, if not the ' +
        'immediate containing dir.'
    )

    parser.add_argument(
        '--batch_size',
        default=0,
        help='The maximum batch to store before writing into the staging ' +
        'environment. Set to 0 for no maximum batch size.'
    )

    parser.add_argument(
        '--overwrite',
        default=False,
        action='store_true',
        help='A flag to specify overwriting existing PREMIS records. ' +
        'Defaults to False.'
    )

    parser.add_argument(
        '--premis',
        default=False,
        action='store_true',
        help='Create premis records for files ending in .premis.xml.' +
        'Defaults to False.'
    )

    parser.add_argument(
        '--fits',
        default=False,
        action='store_true',
        help='Create premis records for files ending in .fits.xml.' +
        'Defaults to False.'
    )

    args = parser.parse_args

    # Begin app code
    stagereader = build_stage_reader(args.path, args.root)
    file_suites = stagereader.file_suites_fullpaths

    records = []

    for x in file_suites:
        if x.premis and not args.overwrite:
            continue
        if not args.fits and StageReader.re_trailing_fits.search(x.original):
            continue
        if not args.premis and \
                StageReader.re_trailing_premis.search(x.original):
            continue

        record = build_record(x.original)
        path = join(stagereader.root_fullpath,
                    stagereader.hypothesize_premis_from_orig_node(
                        stagereader.fpt.tree.get_node(x.original)
                    )
                    )
        tup = (record, path)
        records.append(tup)
        if args.batch_size:
            if len(records) >= args.batch_size:
                write_records(records)
    write_records(records)

if __name__ == '__main__':
    main()
