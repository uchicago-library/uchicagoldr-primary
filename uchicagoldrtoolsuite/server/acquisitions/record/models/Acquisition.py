

from ..database import db

class Acquisition(db.Model):
    __table__ = db.Model.metadata.tables['Acquisition']