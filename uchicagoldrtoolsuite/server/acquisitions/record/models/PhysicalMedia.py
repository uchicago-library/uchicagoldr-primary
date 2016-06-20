from ..database import db

class PhysicalMedia(db.Model):
    __table__ = db.Model.metadata.tables['PhysicalMedia']