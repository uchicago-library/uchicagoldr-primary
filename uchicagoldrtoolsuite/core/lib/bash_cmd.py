from subprocess import run, PIPE, STDOUT, TimeoutExpired


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class BashCommand(object):
    args = []
    status = None
    cmd_out = None
    data = None
    timeout = None
    command_ran = False
    command_completed = False

    def __init__(self, arguments):
        self.args = arguments

    def run_command(self):
        assert isinstance(self.args, list)
        try:
            cmd = run(self.args, stdout=PIPE, stderr=STDOUT,
                      timeout=self.timeout, universal_newlines=True)
            self.command_ran = True
            self.command_completed = True
        except TimeoutExpired as e:
            cmd = e
            self.command_ran = True
            self.cmd_out = e
            self.command_completed = False
            return(True, e, False)
        except Exception as e:
            self.cmd_out = e
            return(False, e, False)
        try:
            self.cmd_out = cmd
        except Exception as e:
            self.cmd_out = e
            return (False, e, False)
        return (True, cmd, True)

    def get_data(self):
        return (self.command_ran, self.cmd_out, self.command_completed)

    def get_args(self):
        return self.args

    def set_args(self, new_args):
        assert isinstance(new_args, list)
        self.args = new_args

    def set_timeout(self, new_timeout):
        self.timeout = new_timeout

    def get_timeout(self):
        return self.timeout
