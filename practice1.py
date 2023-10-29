import MySQLdb
import logging
from connect import Connect
from validation import IntegerInputValidator, MinimumLengthValidator

logger = logging.getLogger(__name__)


class Provider(object):
    """Provider CRUD operations"""

    def __init__(self):
        self.int_validator = IntegerInputValidator()
        self.min_validator = MinimumLengthValidator()

    def insert(self, providers_list):
        try:
            conn = Connect()
            cursor = conn.db.cursor()
            cursor.executemany(
                """
                INSERT INTO providers (name, address, phone)
                    VALUES (%(name)s, %(address)s, %(phone)s)
                """, providers_list
            )
            conn.db.commit()
            logger.info('Provider %02d inserted' % cursor.lastrowid)
        except MySQLdb.MySQLError as e:
            logger.error('Could not insert provider: %s' % e)
        finally:
            conn.db.close()

    def retrieve(self, provider_id):
        result = None
        try:
            conn = Connect()
            cursor = conn.db.cursor()
            cursor.execute(
                """
                SELECT * FROM providers WHERE providerID=%(id)s
                """, {'id': provider_id}
            )
            result = cursor.fetchall()
        except MySQLdb.MySQLError as e:
            logger.error('Could not retrieve the records: %s' % e)
        finally:
            conn.db.close()
        return result

    def update(self, **kwargs):
        self.min_validator.validate(kwargs.get('name'), 3)
        self.int_validator.validate(kwargs.get('id'))
        try:
            conn = Connect()
            result = conn.db.cursor().execute(
                """
                UPDATE providers
                    SET name=%(name)s, address=%(address)s, phone=%(phone)s
                WHERE providerID=%(id)s AND EXISTS (
                    SELECT providerID FROM (
                        SELECT providerID FROM providers WHERE providerID=%(id)s
                    ) AS tmp
                )
                """, kwargs
            )
            conn.db.commit()

            if result:
                logger.info('Provider id %02d updated' % kwargs.get('id'))
            else:
                logger.info('Could not update provider')
        except MySQLdb.MySQLError as e:
            logger.error('Could not update provider: %s' % e)
        finally:
            conn.db.close()

    def delete(self, provider_id):
        try:
            conn = Connect()
            result = conn.db.cursor().execute(
                """
                DELETE FROM providers WHERE providerID=%(id)s
                """ % {'id': provider_id}
            )
            conn.db.commit()
            if result:
                logger.warning('provider id %02d deleted' % provider_id)
            else:
                logger.warning('Provider does not exist')
        except MySQLdb.MySQLError as e:
            logger.error('Could not delete provider: %s' % e)
        finally:
            conn.db.close()
