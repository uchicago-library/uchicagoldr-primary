from ..database import db

class Origin(db.Model):
    __table__ = db.Model.metadata.tables['Origin']