import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


SERVER_NAME = os.environ.get('SERVER_NAME', 'localhost')

DATABASE = {
    'db': os.environ.get('db'),
    'user': os.environ.get('user'),
    'passwd': os.environ.get('passwd'),
    'host': os.environ.get('host', 'localhost'),
    'port': int(os.environ.get('port', 3306)),
    'ssl': {
        'ca': os.environ.get('ca'),
        'cert': os.environ.get('cert'),
        'key': os.environ.get('key'),
    }
}

PASSWORD_HASHER = 'Argon2PasswordHasher'
