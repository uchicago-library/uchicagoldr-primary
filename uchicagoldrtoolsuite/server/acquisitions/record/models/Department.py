from ..database import db

class Department(db.Model):
    __table__ = db.Model.metadata.tables['Department']