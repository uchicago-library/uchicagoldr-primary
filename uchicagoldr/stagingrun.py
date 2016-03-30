from os import listdir
from os.path import join

class StagingRun(object):
    def __init__(self, prefix, stage_id, dest_root):
        self.prefix = prefix
        self.stage_id = stage_id
        self.destination_root = dest_root
        self.current_run = self.set_current_run()

    def set_current_run(self):
        path = join(self.destination_root, self.stage_id)
        if path:
            datadirs = [x for x in listdir(join(path, 'data'))
                        if self.prefix in x]
            admindirs = [x for x in listdir(join(path, 'admin'))
                         if self.prefix in x]
            if len(set(datadirs) - set(admindirs)) > 0:
                raise ValueError("There is a mismatch between data dir and admin dir " +
                                 "where there are {} directories with prefix {}".\
                                 format(len(datadirs), self.prefix) +
                                 " in the data dir and {} directories " +\
                                 "with that prefix in admin")
            elif len(datadirs) == 0 and len(admindirs) == 0:
                self.current_run = self.prefix + '1'
            else:
                number = datadirs[-1].replace(self.prefix,'')
                number = str(int(number) + 1)
                self.current_run = self.prefix + number
        else:
            self.current_run = self.prefix + '1'

        
    def get_current_run(self):
        print(self.current_run)
        return self.current_run
