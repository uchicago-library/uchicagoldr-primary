from ..database import db

class Collection(db.Model):
    __table__ = db.Model.metadata.tables['Collection']