from ..database import db

class Spool(db.Model):
    __table__ = db.Model.metadata.tables['Spool']