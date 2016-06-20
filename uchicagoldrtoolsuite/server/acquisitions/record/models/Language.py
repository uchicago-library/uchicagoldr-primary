from ..database import db

class Language(db.Model):
    __table__ = db.Model.metadata.tables['Language']