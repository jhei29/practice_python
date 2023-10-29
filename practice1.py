import argon2
import bcrypt
import hashlib
import secrets
import binascii


class Argon2PasswordHasher:
    """
    Secure password hashing using the argon2 algorithm.

    This is the winner of the Password Hashing Competition 2013-2015
    (https://password-hashing.net). It requires the argon2-cffi library which
    depends on native C code and might cause portability issues.
    """
    time_cost = 2
    memory_cost = 512
    parallelism = 2

    def encode(self, password, salt):
        data = argon2.low_level.hash_secret(
            password.encode(),
            salt.encode(),
            time_cost=self.time_cost,
            memory_cost=self.memory_cost,
            parallelism=self.parallelism,
            hash_len=argon2.DEFAULT_HASH_LENGTH,
            type=argon2.low_level.Type.I,
        )
        return data.decode('ascii')

    def verify(self, password, encoded):
        try:
            return argon2.low_level.verify_secret(
                encoded.encode('ascii'),
                password.encode(),
                type=argon2.low_level.Type.I,
            )
        except argon2.exceptions.VerificationError:
            return False


class BCryptSHA256PasswordHasher:
    """
    Secure password hashing using the bcrypt algorithm (recommended)

    This is considered by many to be the most secure algorithm but you
    must first install the bcrypt library.  Please be warned that
    this library depends on native C code and might cause portability
    issues.
    """
    digest = None
    rounds = 12

    def salt(self):
        return bcrypt.gensalt(self.rounds)

    def encode(self, password, salt):
        password = password.encode()
        if self.digest is not None:
            password = binascii.hexlify(self.digest(password).digest())

        data = bcrypt.hashpw(password, self.salt())
        return hashlib.sha1(password).hexdigest()

    def verify(self, password, encoded):
        encoded_2 = self.encode(password)
        return secrets.compare_digest(encoded.encode(), encoded_2.encode())


class UnsaltedMD5PasswordHasher:
    """
    The unsalted MD5 password hashing algorithm.
    Incredibly insecure algorithm that you should *never* use
    """

    def encode(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    def verify(self, password, encoded):
        encoded_2 = self.encode(password)
        return secrets.compare_digest(encoded.encode(), encoded_2.encode())


class PlainTextPassword:
    """
    Non-hashing plaintext password (for test only)
    """

    def encode(self, password, salt):
        return password

    def verify(self, password, encoded):
        return password == encoded
