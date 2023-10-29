import argon2
import bcrypt
import hashlib
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

    rounds = 12

    def salt(self):
        return bcrypt.gensalt(self.rounds).decode()

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
    digest = hashlib.sha256
    rounds = 12

    def salt(self):
        return bcrypt.gensalt(self.rounds)

    def encode(self, password, salt):
        password = password.encode()
        if self.digest is not None:
            password = binascii.hexlify(self.digest(password).digest())

        data = bcrypt.hashpw(password, salt)
        return data.decode('ascii')

    def verify(self, password, encoded):
        try:
            password = binascii.hexlify(
                self.digest(password.encode()).digest())
            return bcrypt.checkpw(password, encoded.encode('ascii'))
        except Exception:
            return False
