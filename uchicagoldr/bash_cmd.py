
from subprocess import run, PIPE, STDOUT


class BashCommand(object):
    args = []
    status = None
    cmd_out = None
    data = None
    timeout = None
    command_ran = False

    def __init__(self, arguments):
        self.args = arguments

    def run_command(self):
        assert isinstance(self.args, list)
        try:
            cmd = run(self.args, stdout=PIPE, stderr=STDOUT,
                      timeout=self.timeout, universal_newlines=True)
            self.command_ran = True
        except Exception as e:
            self.cmd_out = e
            return(False, e)
        try:
            self.cmd_out = cmd
        except Exception as e:
            self.cmd_out = e
            return (False, e)
        return (True, cmd)

    def get_data(self):
        return (self.command_ran, self.cmd_out)

    def get_args(self):
        return self.args

    def set_args(self, new_args):
        assert isinstance(new_args, list)
        self.args = new_args

    def set_timeout(self, new_timeout):
        self.timeout = new_timeout

    def get_timeout(self):
        return self.timeout
