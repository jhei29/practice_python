import os

BASE_DIR = os.environ.get('BASE_DIR')

PROFILES_DIR = os.path.join(BASE_DIR, 'profiles')


DEV_MODE = os.environ.get(BASE_DIR, False)


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
    },
    'ssl_mode': 'REQUIRED'
}


PASSWORD_HASHER = 'BCryptSHA256PasswordHasher'


ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'auth.securecodewarrior.com')


# Symmetric Encryption and Decryption Key

SECRET_KEY = os.environ.get('SECRET_KEY')


# Asymmetric Encryption and Decryption RSA Keys

PRIVATE_KEY = os.environ.get('PRIVATE_KEY')

PUBLIC_KEY = os.environ.get('PUBLIC_KEY')


# AWS S3 Storage

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')

AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=%s' % os.environ.get('CacheControl'),
}

AWS_LOCATION = os.environ.get('AWS_LOCATION')
