import MySQLdb
import logging
from config import DATABASE

logger = logging.getLogger(__name__)


class Connect(object):
    """Connect to the database"""

    def __init__(self):
        try:
            self.db = MySQLdb.connect(**DATABASE)
        except Exception as e:
            logger.error(
                'Database connection error: %s.'
                ' Connection: %s' % (e, DATABASE))
