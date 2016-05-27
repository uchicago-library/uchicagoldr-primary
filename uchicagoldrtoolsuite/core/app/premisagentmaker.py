from os import getcwd
from os.path import expanduser, expandvars, join
from sys import stdout

from pypremis.lib import PremisRecord

from .abc.cliapp import CLIApp
from ..lib.premisagentcreator import PremisAgentCreator


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
    """
    entry point launch hook
    """
    app = PremisAgentUtil(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class PremisAgentUtil(CLIApp):
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(
            description="The UChicago LDR Tool Suite utility " +
            "for creating PREMIS agent records.",
            epilog="{}\n".format(self.__copyright__) +
            "{}\n".format(self.__author__) +
            "{}".format(self.__email__)
        )

        self.parser.add_argument(
            "agentIdentifierType",
            help="The type of the agentIdentifier",
            type=str
        )

        self.parser.add_argument(
            "agentIdentifierValue",
            help="The value of the agentIdentifier",
            type=str
        )

        self.parser.add_argument(
            "agentName",
            help="The name of the agent",
            type=str
        )

        self.parser.add_argument(
            "agentType",
            help="The type of the agent",
            type=str
        )

        self.parser.add_argument(
            "--department",
            help="Department(s) the agent belongs to.",
            type=str,
            action="append",
            default=None
        )

        self.parser.add_argument(
            "--cnet",
            help="CNET of the agent.",
            type=str,
            default=None
        )

        self.parser.add_argument(
            "--agentRole",
            help="The role(s) of the agent",
            type=str,
            action="append",
            default=None
        )

        self.parser.add_argument(
            "--outdir",
            help="The directory path to write the agent record to. " +
            "The default is the current directory.",
            type=str,
            default=None
        )

        # Parse arguments into args namespace
        args = self.parser.parse_args()

        if args.outdir:
            args.outdir = expandvars(expanduser(args.outdir))
        else:
            args.outdir = getcwd()

        # App Code

        a = PremisAgentCreator.make_agent(
            args.agentIdentifierType,
            args.agentIdentifierValue,
            args.agentName,
            args.agentType,
            department=args.department,
            cnet=args.cnet,
            agentRole=args.agentRole
        )

        p = PremisRecord(agents=[a])

        target_file = join(args.outdir, args.agentIdentifierValue+".premis.xml")
        p.write_to_file(
            target_file
        )
        stdout.write(target_file+"\n")
