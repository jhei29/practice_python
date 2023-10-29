import MySQLdb
import logging
import xmltodict
import logging.config
from connect import Connect
from xml.sax import handler, make_parser
from xml.dom import pulldom

logger = logging.getLogger(__name__)


class ProviderXML:
    """Provider XML operations"""

    def insert(self, provider_xml):

        parser = make_parser()
        # Include all external general (text) entities.
        parser.setFeature(handler.feature_external_ges, True)
        # Include all external parameter entities, including the external DTD.
        parser.setFeature(handler.feature_external_pes, False)
        # Report all validation errors
        parser.setFeature(handler.feature_validation, False)

        try:
            document = pulldom.parse(provider_xml, parser=parser)
        except Exception as e:
            logger.error('XML parse error - %s' % e)
            raise ValueError(e) from e
        provider = self._xml_convert(document)

        try:
            conn = Connect()
            cursor = conn.db.cursor()
            cursor.execute(
                """
                INSERT INTO providers (name, address, phone)
                    VALUES (%(name)s, %(address)s, %(phone)s)
                """, provider
            )
            conn.db.commit()
            logger.info('Provider %02d inserted' % cursor.lastrowid)
        except MySQLdb.MySQLError as e:
            logger.error('Could not insert provider: %s' % e)
        finally:
            conn.db.close()

    def _xml_convert(self, document):

        xml = ''
        for event, node in document:
            if event == pulldom.START_ELEMENT:
                expanded_node = document.expandNode(node)
                if expanded_node:
                    xml += expanded_node
                xml += node.toxml()

        data = xmltodict.parse(xml)
        key, value = list(data.items())[0]

        return value
