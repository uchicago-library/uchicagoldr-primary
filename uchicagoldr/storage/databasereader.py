
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class DB(object):
    url = 'mysql+mysqlconnector://ldr:JaQhXZZ5ZB8V3Gsu@duodecimo.lib." + \
    "uchicago.edu:3306/ldr_development'
    
    def _init__(self):
        engine = create_engine(self.url)
        base = declarative_base()

    def reflect_db_tables(self):
        metadata = MetaData()
        metadata.reflect(bind = self.engine)
        return metadata

    def open_session(self):
        session = sessionmaker()
        session.configure(bind = self.engine)
        return session

    def close_session(self, session):
        return session.close()
