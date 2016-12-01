from argparse import ArgumentParser
from sys import stdout, stderr
from os.path import isabs, join, isdir, isfile, exists, split, expanduser, \
    expandvars
from os import makedirs
from abc import ABCMeta
from logging import getLogger

from uchicagoldrtoolsuite import activate_master_log_file, \
    activate_job_log_file, activate_stdout_log, log_aware
from .abc.app import App


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class CLIApp(App, metaclass=ABCMeta):
    """
    The base class for CLI applications, from which specific
    applications should be derived.

    __Provided Methods__

    * spawn_parser (ArgumentParser): Creates the parser boilerplate,
    with the command line flags that all applications set."
    * Prompts
        * prompt (*): Prompt the user for an arbitrary something (usually a str)
        and get their response. The most general user interaction method.
        * bool_prompt (bool/None): Prompt the user for a boolean answer and
        get their response
        * choose_from_prompt (*): Ask the user to choose an element from a list
        * path_prompt (str): Ask the user for a path, get one
    * Prints
        * stdoutp: Print something to standard output
        * stderrp: Print something to standard error
    * Utility
        * create_path: Makes a file or a dir at some path
    """
    @log_aware(log)
    def spawn_parser(self, **kwargs):
        log.debug("Constructing default CLI app argument parser")
        parser = ArgumentParser(**kwargs)

        # Always allow the user to specify an alternate conf dir
        parser.add_argument(
            '--conf_path',
            action='append',
            help="Specify a custom configuration path to be parsed "
            "with precedence over the default and builtin configs.",
            default=[]
        )
        parser.add_argument(
            '--disable_builtin_conf',
            action='store_false',
            help='Disable parsing of the builtin configuration'
        )
        parser.add_argument(
            '--disable_default_conf',
            action='store_false',
            help='Disable parsing of the default configuration'
        )
        # Always allow the user to specify verbosity
        parser.add_argument(
            '-v',
            '--stdout_log_verbosity',
            help="Specify the verbosity of the stdout log. Default: 'INFO'" +
            "Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', " +
            "'DISABLE'.",
            default='INFO'
        )
        parser.add_argument(
            '--disk_log_verbosity',
            help="Specify the verbosity of disk logs. Default: 'DEBUG'. " +
            "Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', " +
            "'DISABLE'.",
            default='DEBUG'
        )
        parser.add_argument(
            '--logdir',
            help="Specify the directory in which to store the audit logs",
            default=None
        )
        parser.add_argument(
            '--max_log_size',
            type=int,
            help="Specify the maximum size of audit logs, in bytes. " +
            "Default: 1GB",
            default=1000000000
        )
        parser.add_argument(
            '--max_log_backups',
            type=int,
            help="Specify the maximum number of backups logs. Default: 4",
            default=4
        )
        self.parser = parser

    @log_aware(log)
    def process_universal_args(self, args):
        log.debug("Processing and acting on arguments from the default " +
                  "CLI app argument parser")
        self.conf = self.build_conf(
            [self.expand_path(x) for x in args.conf_path],
            args.disable_default_conf,
            args.disable_builtin_conf
        )
        logdir = None
        if args.logdir:
            logdir = args.logdir
        if logdir is None:
            logdir = self.conf.get('Logging', 'log_dir_path', fallback=None)
        if logdir:
            logdir = self.expand_path(logdir)
        if logdir is not None:
            job_logdir = join(logdir, "jobs")
        else:
            job_logdir = None
        if args.disk_log_verbosity is not "DISABLE":
            activate_master_log_file(logdir=logdir,
                                     max_log_size=args.max_log_size,
                                     num_backups=args.max_log_backups,
                                     verbosity=args.disk_log_verbosity)
            activate_job_log_file(job_logdir=job_logdir,
                                  verbosity=args.disk_log_verbosity)
        if args.stdout_log_verbosity is not "DISABLE":
            activate_stdout_log(verbosity=args.stdout_log_verbosity)

    @staticmethod
    def expand_path(p):
        return expandvars(expanduser(p))

    def prompt(self, prompt, default=None, disp_default=None, closing=None):
        if not disp_default:
            disp_default = str(default)
        if not default:
            disp_prompt = "{}: ".format(prompt)
        else:
            disp_prompt = "{} ({}): ".format(prompt, disp_default)
        answer = input(disp_prompt)
        if answer == '':
            answer = default
        if closing:
            stdout.write("{}\n".format(closing))

        return answer

    def bool_prompt(self, prompt, default=None, closing=None):
        pos_in = ['t', 'true', 'y', 'yes', '1', 1, True]
        neg_in = ['f', 'false', 'n', 'no', '0', 0, False]
        if default not in pos_in + neg_in and default is not None:
            raise AssertionError('bool_input is for getting bools.')
        answer = self.prompt(prompt, default=default, closing=closing)
        if answer in pos_in:
            return True
        elif answer in neg_in:
            return False
        elif answer is None:
            return None
        else:
            return IOError()

    def choose_from_prompt(self, prompt, choices, choice_str_list=None,
                           default=None, closing=None):
        if choice_str_list is None:
            choice_str_list = []
            for i, x in enumerate(choices):
                choice_str_list.append("{}) {}".format(str(i), str(x)))
            choice_str = "\n".join(choice_str_list)
        else:
            for i, x in enumerate(choice_str_list):
                choice_str_list[i] = "{}) {}".format(str(i), x)
            choice_str = "\n".join(choice_str_list)
        prompt = "{}\n{}\n".format(prompt, choice_str) + \
            "Selection"
        answer = self.prompt(prompt, default=default, closing=closing)
        if isinstance(answer, str):
            for x in answer:
                if x not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    answer = None
                break
            if answer is not None:
                answer = int(answer)
        if answer is None:
            return None
        else:
            return choices[answer]

    def path_prompt(self, prompt, default=None, closing=None,
                    disp_default=None, must_exist=False, must_be_absolute=False,
                    must_be_relative=False, root=None, must_be_file=False,
                    must_be_dir=False):
        prompt = "{}\nPath".format(prompt)
        answer = self.prompt(prompt, default=default, disp_default=disp_default,
                             closing=closing)
        if must_be_absolute:
            if not isabs(answer):
                return False
        if must_be_relative:
            if isabs(answer):
                return False
        if root:
            testpath = join(root, answer)
        else:
            testpath = answer
        if must_exist:
            if not exists(testpath):
                return False
        if must_be_file:
            if not isfile(testpath):
                return False
        if must_be_dir:
            if not isdir(testpath):
                return False
        return answer

    def create_path(self, file_or_dir, path=None):
        if file_or_dir != 'dir' and file_or_dir != 'file':
            raise AssertionError('Specify either \'file\' or \'dir\'')
        if path is None:
            if file_or_dir == 'dir':
                diropt = True
                fileopt = False
            else:
                fileopt = True
                diropt = False
            path = self.path_prompt("Please specify a path to create",
                                    must_be_absolute=True,
                                    must_be_file=fileopt,
                                    must_be_dir=diropt)
            if not path:
                return False
        if file_or_dir == 'file':
            cdir = split(path)[0]
            if not exists(cdir):
                makedirs(cdir)
            if not exists(path):
                open(path, 'w').close()
            return True
        if file_or_dir == 'dir':
            if not exists(path):
                makedirs(path)
            return True

    def stdoutp(self, message, end='\n', sanitize=True):
        if sanitize:
            message = str(message)
            end = str(end)
        stdout.write(message+end)

    def stderrp(self, message, end='\n', sanitize=True):
        if sanitize:
            message = str(message)
            end = str(end)
        stderr.write(message+end)
