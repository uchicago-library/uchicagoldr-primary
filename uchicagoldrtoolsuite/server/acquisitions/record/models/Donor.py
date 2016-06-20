from ..database import db

class Donor(db.Model):
    __table__ = db.Model.metadata.tables['Donor']