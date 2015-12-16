
from uchicagoldr.storage.models import engine
from sqlalchemy.orm import sessionmaker

class Session(object):
    sesh = sessionmaker().configure(bind = engine)

    def open(self):
        sesh = sessionmaker()
        sesh.configure(bind = engine)
        return sesh()

    def close(self):
        self.open.close()
