from .base import *


DEBUG = False




ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]




DATABASES = {

"default": {

"ENGINE": config("PDB_ENGINE"),

"NAME": config("PDB_NAME"),

"USER": config("PDB_USER"),

"PASSWORD": config("PDB_PASSWORD"),

"HOST": config("PDB_HOST"),

"PORT": config("PDB_PORT"),

}

}


