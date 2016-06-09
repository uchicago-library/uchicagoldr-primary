from ..database import db

class PremisAgent(db.Model):
    __table__ = db.Model.metadata.tables['PremisAgent']
