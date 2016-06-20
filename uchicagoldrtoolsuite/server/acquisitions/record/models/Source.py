from ..database import db

class Source(db.Model):
    __table__ = db.Model.metadata.tables['Source']