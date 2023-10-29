import secrets
import MySQLdb
import logging
import importlib
from datetime import datetime
from exception import InputError
from database.connect import Connect
from config import PASSWORD_HASHER, DEV_MODE
from validation import MIN_EMAIL_LENGTH, PasswordValidator, MinimumLengthValidator, UsernameValidator

logger = logging.getLogger(__name__)


class Register:
    """User Registration"""

    def __init__(self, data, *args, **kwargs):
        self.data = data
        self.password_validator = PasswordValidator()
        self.username_validator = UsernameValidator()
        self.min_validator = MinimumLengthValidator()
        # load password hasher class
        hasher = getattr(importlib.import_module('hashers'), PASSWORD_HASHER)
        self.password_hasher = hasher()
        self.salt = secrets.token_hex(32).encode()

    def fields_validation(self, *args, **kwargs):
        username = self.data.get('username').strip()
        self.username_validator.validate(username)

        password1 = self.data.get('password1')
        password2 = self.data.get('password2')
        if password1 != password2:
            raise InputError(
                "The two password fields didn't match.", 'password_mismatch')
        self.password_validator.validate(password1)

        email = self.data.get('email')
        email_confirm = self.data.get('email_confirm')
        if email != email_confirm:
            raise InputError(
                'Both email addresses fields must match.', 'email_mismatch')
        self.min_validator.validate(email, MIN_EMAIL_LENGTH)

    def create(self):
        # validate
        self.fields_validation()
        # password validation
        password = self.data.get('password1')

        encoded_password = self.password_hasher.encode(
            password)

        new_user = {
            'username': self.data.get('username'),
            'password': encoded_password,
            'email': self.data.get('email'),
            'date_joined': datetime.utcnow().isoformat()
        }

        return new_user

    def save(self):
        user = self.create()
        if user:
            try:
                conn = Connect()
                cursor = conn.db.cursor()
                cursor.execute(
                    """
                    INSERT INTO user (username, password, email, date_joined)
                        VALUES (%(username)s, %(password)s,
                                %(email)s, %(date_joined)s)
                    """, user
                )
                conn.db.commit()
                logger.info('User %02d inserted' % cursor.lastrowid)

                if DEV_MODE:
                    logger.debug(
                        '%(username)s, %(password)s, '
                        '%(email)s, %(date_joined)s' % user)

            except MySQLdb.MySQLError as e:
                logger.error('Could not insert provider: %s' % e)
            finally:
                conn.db.close()
