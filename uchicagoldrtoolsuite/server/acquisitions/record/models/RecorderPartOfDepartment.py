from ..database import db

class RecorderPartOFDepartment(db.Model):
    __table__ = db.Model.metadata.tables['RecorderPartOFDepartment']