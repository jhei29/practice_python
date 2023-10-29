import logging
from MySQLdb import MySQLError
from database.connect import Connect

from auth import Auth
from decorators import is_authorized
from serializers import ClientSerializer, AddressSerializer

logger = logging.getLogger(__name__)


class Client(Auth):

    @is_authorized
    def retrieve(self, uuid):

        result = None

        conn = Connect()
        try:
            cursor = conn.db.cursor()
            cursor.execute(
                """
                SELECT first_name, last_name, email, phone
                FROM clients
                WHERE uuid=UUID_TO_BIN(%(uuid)s)
                """, {'uuid': uuid}
            )
            result = cursor.fetchone()
        except MySQLError:
            logger.error('Could not retrieve the client')
        finally:
            conn.db.close()
        return result

    @is_authorized
    def update(self, id, **kwargs):

        result = None
        fields = ClientSerializer().updatefields(kwargs)
        if not fields:
            return result

        if not kwargs.get('id'):
            kwargs.update({'id': id})

        conn = Connect()
        try:
            cursor = conn.db.cursor()
            cursor.execute(
                f"""
                UPDATE clients SET {fields}
                WHERE id=%(id)s
                """, kwargs
            )
            conn.db.commit()
            result = cursor.rowcount

            if not result:
                raise MySQLError

        except MySQLError:
            logger.error('Client could not be updated')
        finally:
            conn.db.close()
        return result

    @is_authorized
    def insert_address(self, **kwargs):

        result = None

        columns, values = AddressSerializer().insertfields(kwargs)
        if not (columns and values):
            return result

        conn = Connect()
        try:
            cursor = conn.db.cursor()
            cursor.execute(
                f"""
                INSERT INTO addresses ({columns})
                VALUES ({values})
                """, kwargs
            )
            conn.db.commit()
            logger.info('Address %02d inserted' % cursor.lastrowid)
        except MySQLError:
            logger.error('Could not insert the address')
        finally:
            conn.db.close()
        return result
