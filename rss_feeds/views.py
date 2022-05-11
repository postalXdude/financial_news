import requests
from io import StringIO
from datetime import datetime

from django.http import JsonResponse, HttpResponseNotFound
from rest_framework.decorators import api_view, parser_classes
from rest_framework import generics
from rest_framework.parsers import JSONParser
from rest_framework_xml.parsers import XMLParser

from .models import Symbols
from .serializers import NewsSerializer, SymbolsSerializer


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


# TODO(Nikola): Is it possible to pass multiple symbols?
class SymbolsCreate(generics.CreateAPIView):
    queryset = Symbols.objects.all(),
    serializer_class = SymbolsSerializer


@api_view(['POST'])
@parser_classes([JSONParser])
def store_new_symbols(request):
    """
    Store new symbols that will be used for fetching Yahoo RSS feeds.
    """
    # TODO(Nikola): Check request body.
    symbols_serializer = SymbolsSerializer(data=request.data, many=True)
    symbols_serializer.is_valid(raise_exception=True)
    symbols_serializer.save()
    # TODO(Nikola): Skip already saved symbols?
    return JsonResponse(symbols_serializer.data, status=201, safe=False)


@api_view(['POST'])
def store_rss_feed_from_source(request, symbol):
    """
    Store RSS feeds from Yahoo in db for desired symbol.
    """
    try:
        Symbols.objects.get(name=symbol)
    except Symbols.DoesNotExist:
        return HttpResponseNotFound(f'Symbol `{symbol}` does not exists!')
    # TODO(Nikola): Randomize headers?
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4482.0 '
                             'Safari/537.36 Edg/92.0.874.0'}
    # TODO(Nikola): Retry on timeouts, http errors, etc.
    response = requests.get(
        'https://feeds.finance.yahoo.com/rss/2.0/headline',
        params={'s': symbol},
        headers=headers,
    )
    # XMLParser expects file object.
    # No need to close it, as it is closed on garbage collection(file is in memory).
    xml_file_object = StringIO(response.text)
    xml_parser = RSSFeedXMLParser()
    # TODO(Nikola): Skip if there are no items?
    items = xml_parser.parse(xml_file_object)
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
    # TODO(Nikola): Skip already saved news?
    return JsonResponse(news_serializer.data, status=201, safe=False)
