import os

class Development():
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("DEBUG")
    FLASK_APP = os.getenv("FLASK_APP")
    FLASK_ENV = os.getenv("FLASK_ENV")
    

class Production():
    SQLALCHEMY_DATABASE_URI = "postgresql://wqsvbcbvszvkxi:de81e26baa5b0b4a8d7ec3ec0cbc0e9617d8a8e9a20cc9c62de166118ab6945a@ec2-54-76-43-89.eu-west-1.compute.amazonaws.com:5432/dccs4uikrqga4a"

    SECRET_KEY = 'LongAndRandomSecretKey'