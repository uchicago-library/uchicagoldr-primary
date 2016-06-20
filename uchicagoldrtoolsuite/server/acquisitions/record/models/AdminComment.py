from ..database import db

class AdminComment(db.Model):
    __table__ = db.Model.metadata.tables['AdminComment']