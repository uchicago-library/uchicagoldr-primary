from os.path import abspath, join, exists
from uchicagoldrtoolsuite.core.lib.confreader import ConfReader

creader = ConfReader()

DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
DATABASE_HOST = creader.get('Database', 'db_host')
DATABASE_USER = creader.get('Database', 'db_user')
DATABASE_PASS = creader.get('Database', 'db_pass')
DATABASE_NAME = creader.get('Database', 'db_name')
CSRF_ENABLED = True
SECRET_KEY = b'/5{\xa0\xc2\x89\x9eI\x12+\x19\x97)\xe3Z\xe9\x9d\xect\xf4\x99\xdc\x9e\xf9'
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}/{}".format(DATABASE_USER, DATABASE_PASS,
                                                               DATABASE_HOST, DATABASE_NAME)