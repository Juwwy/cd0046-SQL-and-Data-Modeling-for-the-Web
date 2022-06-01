import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

class DatabaseURI:
    DATABASE_NAME = "juwwy_fyyurdb"
    username = 'postgres'
    password = 'admin'
    url = 'localhost:5432'

data = DatabaseURI()
 
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(data.username, data.password, data.url, data.DATABASE_NAME )
SQLALCHEMY_TRACK_MODIFICATIONS = False

# TODO IMPLEMENT DATABASE URL

