from ..database import db

class InventoryLetter(db.Model):
    __table__ = db.Model.metadata.tables['InventoryLetter']