from ..database import db

class Restriction(db.Model):
    __table__ = db.Model.metadata.tables['Restriction']