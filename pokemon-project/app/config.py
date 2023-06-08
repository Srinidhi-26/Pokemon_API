class Config(object):
    BASE_URL = "http://127.0.0.1:5000"
    SECRET_KEY = "secret"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://pokemon1:pokemon@localhost/pokemon"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAGE_LIMIT = 13
    MAX_PAGE_LIMIT = 1000000
    TOKENS = "pokemon-api"


class ProductionConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
