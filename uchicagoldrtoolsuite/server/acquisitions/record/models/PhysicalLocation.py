from ..database import db

class PhysicalLocation(db.Model):
    __table__ = db.Model.metadata.tables['PhysicalLocation']