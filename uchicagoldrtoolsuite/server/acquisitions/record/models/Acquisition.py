

from ..database import db

class Acquisition(db.Model):
    print(db.Model.metadata.tables)
    __table__ = db.Model.metadata.tables['Acquisition']