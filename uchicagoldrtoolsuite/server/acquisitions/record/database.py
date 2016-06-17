from flask.ext.sqlalchemy import SQLAlchemy
from .__init__ import app

db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)
