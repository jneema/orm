from distutils.debug import DEBUG
from re import T
import secrets
import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'some_secret'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:nyanumba@localhost:5433/duka'
    environment = 'Development'
    DEBUG = True

class Development(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:nyanumba@localhost:5433/duka'
    environment = 'Development'
    DEBUG = True

class Testing(Config):
    DEBUG = False

class Production(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:nyanumba@localhost:5433/duka'
    Debug = False
    environment = 'Production'