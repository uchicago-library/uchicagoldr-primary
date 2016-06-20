from ..database import db

class GiftAcknowledgement(db.Model):
    __table__ = db.Model.metadata.tables['GiftAcknowledgement']