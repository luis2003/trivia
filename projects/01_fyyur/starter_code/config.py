import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# (DONE) IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:dimulstR@localhost:5432/fyyur'

# disable SQLALCHEMY_TRACK_MODIFICATIONS
SQLALCHEMY_TRACK_MODIFICATIONS = False
