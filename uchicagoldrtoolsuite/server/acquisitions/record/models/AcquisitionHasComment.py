from ..database import db

class AcquisitionHasComment(db.Model):
    __table__ = db.Model.metadata.tables['AcquisitionHasComment']