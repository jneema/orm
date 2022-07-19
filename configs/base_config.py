from distutils.debug import DEBUG
from re import T
import secrets
import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'some_secret'
    environment = 'Development'
    DEBUG = True

class Development(Config):
    environment = 'Development'
    DEBUG = True

class Testing(Config):
    DEBUG = False

class Production(Config):
    Debug = False
    environment = 'Production'