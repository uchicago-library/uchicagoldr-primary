from ..database import db

class Person(db.Model):
    __table__ = db.Model.metadata.tables['Person']