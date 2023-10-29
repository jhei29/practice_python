import logging
import importlib
from datetime import datetime
from MySQLdb import MySQLError
from config import PASSWORD_HASHER
from database.connect import Connect

from decorators import is_authorized

logger = logging.getLogger(__name__)


class Auth:
    """User Authentication"""

    def __init__(self):

        self.id = None
        self.is_authenticate = False
        # load password hasher class from config file
        self.hasher = getattr(
            importlib.import_module('hashers'), PASSWORD_HASHER)()

    def login(self, username, password):

        conn = Connect()
        try:
            cursor = conn.db.cursor()
            cursor.execute(
                """
                SELECT id, password FROM users
                WHERE username=%(username)s
                """, {'username': username}
            )
            result = cursor.fetchone()

            if not (result and self.hasher.verify(password, result[1])):
                raise MySQLError

            self.is_authenticate = True
            self.id = result[0]

            cursor.execute(
                """
                UPDATE users
                SET last_login=%(last_login)s
                WHERE id=%(id)s
                """,
                {
                    'last_login': datetime.now(),
                    'id': self.id
                }
            )
            conn.db.commit()
            result = cursor.rowcount

            if not result:
                logger.error('Last login could not be updated')

        except Exception:
            logger.error('Login authorization failure')
        finally:
            conn.db.close()

    def logout(self):

        self.id = None
        self.is_authenticate = False

    @is_authorized
    def roles(self):

        result = None
        conn = Connect()
        try:
            cursor = conn.db.cursor()
            cursor.execute(
                """
                SELECT name FROM roles
                INNER JOIN user_roles ON roles.id = user_roles.role_id
                WHERE user_roles.user_id = %(user_id)s
                """, {'user_id': self.id}
            )
            result = [role[0] for role in cursor.fetchall()]
        except MySQLError:
            logger.error('Could not retrieve the user record')
        finally:
            conn.db.close()
        return result
