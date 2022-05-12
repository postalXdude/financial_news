import requests
from io import StringIO
from datetime import datetime
import logging

from core.celery import app
from fake_useragent import UserAgent
from rest_framework_xml.parsers import XMLParser

from .exceptions import YahooRSSFeedError
from .serializers import NewsSerializer

logger = logging.getLogger(__name__)

UA = UserAgent()


class RSSFeedXMLParser(XMLParser):
    def _xml_convert(self, element):
        """
        Custom converter used specifically to obtain `item` tags from RSS feed.
        Original method is overriding same tag, e.g., it is not handling properly
        list of objects.
        """
        items = []
        for item_tags in element.findall('.//item'):
            item_object = {}
            for item_tag in item_tags:
                item_object.update({item_tag.tag: item_tag.text})
            items.append(item_object)
        return items


@app.task
def fetch_rss_from_source_for_symbol(symbol):
    """
    Store RSS feeds from Yahoo in db for desired symbol.
    """
    # TODO(Nikola): Retry on timeouts, http errors, in task itself?
    response = requests.get(
        'https://feeds.finance.yahoo.com/rss/2.0/headline',
        params={'s': symbol},
        headers={'user-agent': UA.random},
    )
    if response.status_code != 200:
        raise YahooRSSFeedError()
    # XMLParser expects file object.
    # No need to close it, as it is closed on garbage collection(file is in memory).
    xml_file_object = StringIO(response.text)
    xml_parser = RSSFeedXMLParser()
    items = xml_parser.parse(xml_file_object)
    if not items:
        logger.info(f"There are currently no feeds for `{symbol}`!")
        return
    for item in items:
        item.update({
            'symbol': symbol,
            'published_on': item.pop('pubDate')
        })
        # Can not be put in serializer because of sheer complexity of format.
        item['published_on'] = datetime.strptime(
            item['published_on'], '%a, %d %b %Y %H:%M:%S %z')
    news_serializer = NewsSerializer(data=items, many=True)
    news_serializer.is_valid(raise_exception=True)
    news_serializer.save()
