from sys import stdout

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

from .internal.cliapp import CLIApp
from ..lib.accessionrecorder import AccessionRecordConfig, \
    AccessionRecorder


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


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


def launch():
    app = AccessionRecordEditor(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class AccessionRecordEditor(CLIApp):
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for creating original PREMIS object records " +
                          "for materials in staging structures.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("-r",
                            "--record",
                            help="Specify an existing record to read or alter",
                            default=None)
        self.parser.add_argument("-k",
                            "--key",
                            help="Specify a key to act on, when appropriate",
                            default=None)
        self.parser.add_argument("-v",
                            "--value",
                            help="Specify a value, when appropriate.",
                            default=None)
        self.parser.add_argument("-o",
                            "--out",
                            help="Specify an out path, if required and not the same as the original record path.",
                            default=None)
        self.parser.add_argument("-c",
                            "--conf",
                            help="Specify a configuration path, if appropriate.",
                            default=None)
        self.parser.add_argument("--set",
                            help="Set the specified [key] to [value] in the specified [record]. Or a new record if none is specified.",
                            action='store_true',
                            default=False)
        self.parser.add_argument("--add",
                            help="Add the specified [value] to the specified [key] in the specified [record]. Or set a field in a new record if no record is specified.",
                            action='store_true',
                            default=False)
        self.parser.add_argument("--delete",
                            help="Delete the specified [key]",
                            action='store_true',
                            default=False)
        self.parser.add_argument("-p",
                            "--stdout",
                            help="Print the record to stdout at the end of all specified operations.",
                            action='store_true',
                            default=False)
        self.parser.add_argument("--get",
                            help="Get the value of the specified [key] from the specified [record].",
                            action='store_true',
                            default=False)
        self.parser.add_argument("--leaves",
                            help="Print the leaf tuples of the specified [record] to stdout.",
                            action='store_true',
                            default=False)
        self.parser.add_argument("--keys",
                            help="Print the keys of the specified [record] to stdout.",
                            action='store_true',
                            default=False)
        self.parser.add_argument("--values",
                            help="Print the values of the specified [record] to stdout.",
                            action='store_true',
                            default=False)
        self.parser.add_argument("--validate",
                            help="Validate the specified [record] against the specified [conf]iguration.",
                            action='store_true',
                            default=False)
        args = self.parser.parse_args()
        # App code
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
