from uchicagoldrtoolsuite.apps.internals.cliapp import CLIApp

__author__ = "Test Author"
__email__ = "example@testemail.com"
__company__ = "Example Company LLC."
__copyright__ = "Copyright notice here"
__publication__ = "Publication info here"
__version__ = "0.0.0"

def launch():
    TestApp(
        __author__=__author__,
        __email__=__email__,
        __company__=__company__,
        __copyright__=__copyright__,
        __publication__ = __publication__,
        __version__=__version__
    )


class TestApp(CLIApp):
    def main(self):
        # Get our boilerplate parser
        parser = self.spawn_parser()

        parser.add_argument(
            '-e',
            '--example',
            action='store_true',
            default=False,
            help='An example flag added to this application.'
        )

        # Gather all of our args
        args = parser.parse_args()

        # Begin app code
        if args.example and args.verbose == 0:
            self.stdoutp('the example flag is present')

        elif args.example and args.verbose == 1:
            self.stdoutp('Hello, the example flag and a verbose are present.')

        elif args.example and args.verbose == 2:
            self.stdoutp('HELLO, THE EXAMPLE FLAG AND TWO verbose ' +
                  'FLAGS ARE PRESENT.')

        elif args.example and args.verbose >= 3:
            self.stdoutp('HELLO, THE EXAMPLE FLAG AND THREE OR MORE verbose ' +
                  'FLAGS ARE PRESENT.')
            for x in [self.__author__, self.__email__, self.__company__,
                      self.__publication__, self.__version__]:
                self.stdoutp(x)
            self.stdoutp("Your conf dir is: {}".format(str(args.conf_dir)))
            self.stdoutp("Your conf file is: {}".format(str(args.conf_file)))
        else:
            if len(vars(args)) == 0:
                self.stdoutp('This command had no flags passed to it.')
            else:
                self.stdoutp('This command doesnt print anything ' +
                             'when you pass those flags... except ' +
                             'for this.')
