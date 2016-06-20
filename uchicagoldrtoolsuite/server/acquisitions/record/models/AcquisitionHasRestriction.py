from ..database import db

class AcquisitionHasRestriction(db.Model):
    __table__ = db.Model.metadata.tables['AcquisitionHasRestriction']