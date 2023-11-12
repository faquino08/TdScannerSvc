from pathlib import Path
from os import environ
import json

PROJECT_ROOT = environ['PROJECT_ROOT']
POSTGRES_LOCATION = environ['POSTGRES_LOCATION']
POSTGRES_PORT = environ['POSTGRES_PORT']
POSTGRES_DB = environ['POSTGRES_DB']
POSTGRES_USER = environ['POSTGRES_USER']
POSTGRES_PASSWORD = environ['POSTGRES_PASSWORD']
APP_NAME = environ.get('APP_NAME','TdReader')
DEBUG = json.loads(environ['DEBUG_BOOL'].lower())