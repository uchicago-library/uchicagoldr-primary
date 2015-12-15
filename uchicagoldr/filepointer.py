from uuid import uuid4
from os import getcwd
from os.path import exists, join, isdir
from pickle import dump


class FilePointer(object):
    def __init__(self, target):
        if not isinstance(target, str):
            raise TypeError
        self.identifier = str(uuid4())
        self.target = target
        self.hash = hash(target)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return (isinstance(other, FilePointer) and
                hash(self) == hash(other))

    def __repr__(self):
        return "FilePointer object with identifer {}".format(self.identifier)

    def get_identifier(self):
        return self.identifier

    def write_to_file(self, path=getcwd(), file_name=None, clobber=False):
        if file_name is None:
            file_name = self.get_uuid() + '.filepointer'
        assert(isinstance(path, str))
        assert(isinstance(file_name, str))
        assert(isinstance(clobber, bool))
        assert(isdir(path))
        if clobber is False:
            assert(not exists(join(path, file_name)))
        with open(join(path, file_name), 'wb') as f:
            dump(self, f)


    def write_to_db(self):
        pass

    def look_up_file(self):
        # Return a reference to the File object
        pass
