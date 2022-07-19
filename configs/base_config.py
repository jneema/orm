import secrets
import os

class Base:
    FLASK_APP = os.environ.get("FLASK_APP")
    SQLALCHEMY_TRACKMODIFICATIONS = False
    SECRET_KEY = secrets.token_hex(16)

class Development(Base):
    FLASK_ENV= os.environ.get("FLASK_ENV")
    DATABASE = os.environ.get("DATABASE")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    # SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI")

class Staging(Base):
    pass

class Production(Base):
    SQLALCHEMY_DATABASE_URI = "postgresql://wqsvbcbvszvkxi:de81e26baa5b0b4a8d7ec3ec0cbc0e9617d8a8e9a20cc9c62de166118ab6945a@ec2-54-76-43-89.eu-west-1.compute.amazonaws.com:5432/dccs4uikrqga4a"
