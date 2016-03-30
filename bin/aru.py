
from argparse import Action, ArgumentParser
from os import _exit
from sys import stderr, stdout
from uchicagoldr.accessionrecorder import AccessionRecorder, \
    AccessionRecordConfig
from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "University of Chicago"
__copyright__ = "University of Chicago, 2016"
__publication__ = "2016-03-01"
__version__ = "1.0.0"

def add(recorder, args):
    recorder.get_record().add_to_field(args.key, args.value)

def set(recorder, args):
    recorder.get_record()[args.key] = args.value

def delete(recorder, args):
    del recorder.get_record()[args.key]

def get(recorder, args):
    stdout.write(recorder.get_record()[args.key]+'\n')

def leaves(recorder):
    for x in recorder.get_record().leaves():
        stdout.write(str(x)+'\n')

def keys(recorder):
    for x in recorder.get_record().keys():
        stdout.write(str(x)+'\n')

def values(recorder):
    for x in recorder.get_record().values():
        stdout.write(str(x)+'\n')

def validate(recorder):
    result = recorder.validate_record()
    if result[0] == True:
        stdout.write("True")
    else:
        stdout.write("False\n")
        stdout.write(result[1])
    stdout.write("\n")

def write(recorder, args):
    with open(args.out, 'w') as f:
        f.write(recorder.get_record().toJSON())

def build_accession_recorder(args):
    if args.record:
        record = HierarchicalRecord(from_file=args.record)
    else:
        record = HierarchicalRecord()
    if args.conf:
        config = AccessionRecordConfig(args.conf)
    else:
        config = None
    a = AccessionRecorder(record=record, conf=config)
    return a

def set_out(args):
    if args.out:
        return args.out
    elif not args.out:
        if args.record:
            return args.record
        else:
            return None

def make_bools(args):
    if args.value == "False":
        return False
    if args.value == "True":
        return True

def main():
    parser = ArgumentParser(description="A utility for ",epilog="Copyright {copyright}; written by <{email}>.".format(copyright = __copyright__, email = __email__))
    parser.add_argument("-r",
                        "--record",
                        help="Specify an existing record to read or alter",
                        default=None)
    parser.add_argument("-k",
                        "--key",
                        help="Specify a key to act on, when appropriate",
                        default=None)
    parser.add_argument("-v",
                        "--value",
                        help="Specify a value, when appropriate.",
                        default=None)
    parser.add_argument("-o",
                        "--out",
                        help="Specify an out path, if required and not the same as the original record path.",
                        default=None)
    parser.add_argument("-c",
                        "--conf",
                        help="Specify a configuration path, if appropriate.",
                        default=None)
    parser.add_argument("--set",
                        help="Set the specified [key] to [value] in the specified [record]. Or a new record if none is specified.",
                        action='store_true',
                        default=False)
    parser.add_argument("--add",
                        help="Add the specified [value] to the specified [key] in the specified [record]. Or set a field in a new record if no record is specified.",
                        action='store_true',
                        default=False)
    parser.add_argument("--delete",
                        help="Delete the specified [key]",
                        action='store_true',
                        default=False)
    parser.add_argument("-p",
                        "--stdout",
                        help="Print the record to stdout at the end of all specified operations.",
                        action='store_true',
                        default=False)
    parser.add_argument("--get",
                        help="Get the value of the specified [key] from the specified [record].",
                        action='store_true',
                        default=False)
    parser.add_argument("--leaves",
                        help="Print the leaf tuples of the specified [record] to stdout.",
                        action='store_true',
                        default=False)
    parser.add_argument("--keys",
                        help="Print the keys of the specified [record] to stdout.",
                        action='store_true',
                        default=False)
    parser.add_argument("--values",
                        help="Print the values of the specified [record] to stdout.",
                        action='store_true',
                        default=False)
    parser.add_argument("--validate",
                        help="Validate the specified [record] against the specified [conf]iguration.",
                        action='store_true',
                        default=False)
    args = parser.parse_args()
    try:
        a = build_accession_recorder(args)
        args.out = set_out(args)
        args.value = make_bools(args)
        if args.set:
            set(a, args)
        if args.add:
            add(a, args)
        if args.delete:
            delete(a, args)
        if args.get:
            get(a, args)
        if args.leaves:
            leaves(a)
        if args.keys:
            keys(a)
        if args.values:
            values(a)
        if args.validate:
            validate(a)
        if args.set or args.add or args.delete:
            write(a, args)
        if args.stdout:
            print(str(a.get_record()) + '\n')
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
