from ..database import db

class Accession(db.Model):
    __table__ = db.Model.metadata.tables['Accession']