from os.path import abspath, isdir
from pypremis.lib import PremisRecord
from pypremis.nodes import *
from uchicagoldrtoolsuite.apps.internals.cliapp import CLIApp
from uchicagoldrtoolsuite.lib.filewalker import FileWalker
from uchicagoldr.lib.premisextensionnodes import Restriction


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
    app = PremisRestrictionSetter(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


def gather_records(path):
    """
    gather all .premis.xml files from a path

    __Args__

    1. path (str): the path to a dir to search for premis records

    __Returns__
    * (list): A list of tuples formatted as:
        (PremisRecord instance, path)
    """
    records = []
    if isdir(path):
        for x in FileWalker(path, filter_pattern="^.*\.premis.xml$"):
            records.append((load_record(x), x))
    else:
        records.append((load_record(path), path))
    return records


def load_record(path):
    return PremisRecord(frompath=path)


def build_rights_extension_node(restriction_code, restriction_reason=None,
                                donor_stipulation=None, linkingAgentIds=None,
                                active=True):
    rights_extension = RightsExtension()
    rights_extension.add_to_field('Restriction', build_restriction_node(
        restriction_code=restriction_code,
        restriction_reason=restriction_reason,
        donor_stipulation=donor_stipulation,
        linkingAgentIds=linkingAgentIds,
        active=active))
    return rights_extension


def build_restriction_node(restriction_code, active=True,
                           restriction_reason=None, donor_stipulation=None,
                           linkingAgentIds=None):
    restrictionNode = Restriction(restriction_code, active)
    if restriction_reason:
        for x in restriction_reason:
            restrictionNode.add_restrictionReason(x)
    if donor_stipulation:
        for x in donor_stipulation:
            restrictionNode.add_donorStipulation(x)
    if linkingAgentIds:
        for x in linkingAgentIds:
            restrictionNode.add_linkingAgentIdentifier(x)
    return restrictionNode


class PremisRestrictionSetter(CLIApp):
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for setting restrictions in PREMIS files.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument(
            'path',
            help='Specify a path to a premis record, or a path to search for ' +
            'premis records, all of which will be acted upon.'
        )
        self.parser.add_argument(
            'restriction',
            # choices = somecontrolledvocabhere,
            # https://docs.python.org/3/library/argparse.html#choices
            help='Specify the restriction code to apply to all ' +
            'found PREMIS records.'
        )
        self.parser.add_argument(
            '--reason',
            default=None,
            action='append',
            help='Specify the reason for applying the restriction'
        )
        self.parser.add_argument(
            '--donor-stipulation',
            action='append',
            default=None,
            help='Specify a donor stipulation'
        )
        # Parse arguments into args namespace
        args = self.parser.parse_args()
        # App code
        path = abspath(args.path)
        record_tups = gather_records(path)

        for x in record_tups:
            record = x[0]
            rec_path = x[1]
            if record.get_rights_list():
                rights = record.get_rights_list()[0]
                try:
                    rights_extension = rights.get_rightsExtension(0)
                    rights_extension.add_to_field('Restriction',
                                                build_restriction_node(
                                                    args.restriction,
                                                    True,
                                                    args.reason,
                                                    args.donor_stipulation
                                                ))
                except KeyError:
                    rights.add_rightsExtension(build_rights_extension_node(
                                                args.restriction,
                                                True,
                                                args.reason,
                                                args.donor_stipulation
                    ))
            else:
                rights = Rights(rightsExtension=build_rights_extension_node(
                    args.restriction,
                    args.reason,
                    args.donor_stipulation
                ))
                record.add_rights(rights)
            record.write_to_file(rec_path)
