import MySQLdb
import logging
from config import DATABASE

logger = logging.getLogger(__name__)


class Connect(object):
    """Connect to the database"""

    def __init__(self):
        try:
            self.db = MySQLdb.connect(
                db='database_anwUli9rE2RzO', user='admin_kX0AQKBgQDHq',
                passwd='Q!W@E#r4t5y6', **DATABASE)
        except MySQLdb.MySQLError as e:
            logger.error('Database connection error: %s' % e)
