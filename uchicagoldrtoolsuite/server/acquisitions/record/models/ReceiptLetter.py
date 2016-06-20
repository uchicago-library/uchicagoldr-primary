from ..database import db

class ReceiptLetter(db.Model):
    __table__ = db.Model.metadata.tables['ReceiptLetter']