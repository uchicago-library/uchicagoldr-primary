from ..database import db

class Recorder(db.Model):
    __table__ = db.Model.metadata.tables['Recorder']