import hashlib

import requests

from exception import InputError


MIN_EMAIL_LENGTH = 3
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 64
MIN_USERNAME_LENGTH = 8
MAX_USERNAME_LENGTH = 50


class PasswordValidator:
    """
    Validates password to ensure:
    - Minimum and maximum length
    - Password has not been previously breached
    - Usage of all characters including unicode and whitespace is allowed.
    """

    def validate(self, password):
        # Ensure a password minimum length
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InputError(
                'Password minimum length: 8 characters', 'password_too_short')

        # Ensure a password maximum length
        if len(password) > MAX_PASSWORD_LENGTH:
            raise InputError(
                'Password maximum length: 64 characters', 'password_too_long')

        # Check against previously breached passwords
        password_sha1 = hashlib.sha1(
            password.encode('utf-8')).hexdigest().upper()
        try:
            url = f'https://api.pwnedpasswords.com/range/{password_sha1[:5]}'
            response = requests.get(url)
            result_list = response.content.split(b'\r\n')

            for item in result_list:
                if password_sha1[5:] == item.decode().split(':')[0]:
                    raise InputError(
                        'Password found in pwned database!', 'password_breached')
        except Exception as e:
            raise InputError(
                'Error while verifying pwned database!', 'pwned_api_error')


class MinimumLengthValidator:
    """
    Validate whether the input is of a minimum length.
    """

    def validate(self, input, min_length=8):
        message = (
            'This input is too short. '
            'It must contain at least %d character.' % min_length)

        if not input:
            raise InputError(input, message)

        if len(input) < min_length:
            raise InputError(input, message)


class UsernameValidator:
    """
    Validates username to ensure:
    - Minimum and maximum length
    - Only alphanumeric characters
    """

    def validate(self, username):
        # Ensure username minimum length
        if len(username) < MIN_USERNAME_LENGTH:
            raise InputError(
                'Username minimum length: 5 characters', 'username_too_short')

        # Ensure username maximum length
        if len(username) > MAX_USERNAME_LENGTH:
            raise InputError(
                'Username maximum length: 50 characters', 'username_too_long')

        # Ensure username contains only alphanumeric characters
        if not username.isnumeric():
            raise InputError(
                'Username must contain only alphanumeric characters',
                'username_invalid_characters')
