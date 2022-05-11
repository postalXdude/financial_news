from django.http import JsonResponse, HttpResponseNotFound
from rest_framework.decorators import api_view, parser_classes
from rest_framework import generics
from rest_framework.parsers import JSONParser

from .models import Symbols, News
from .serializers import NewsSerializer, SymbolsSerializer


# TODO(Nikola): Is it possible to pass multiple symbols?
class SymbolsCreate(generics.CreateAPIView):
    queryset = Symbols.objects.all(),
    serializer_class = SymbolsSerializer


@api_view(['GET'])
def get_rss_feed_for_symbol(request, symbol):
    """
    Get RSS feeds from Yahoo that are stored db for desired symbol.
    """
    try:
        news = News.objects.get(symbol=symbol)
    except Symbols.DoesNotExist:
        return HttpResponseNotFound(f'Symbol `{symbol}` does not exists!')
    return JsonResponse(news, status=201, safe=False)


@api_view(['POST'])
@parser_classes([JSONParser])
def store_symbols(request):
    """
    Store new symbols that will be used for fetching Yahoo RSS feeds.
    """
    # TODO(Nikola): Check request body.
    symbols_serializer = SymbolsSerializer(data=request.data, many=True)
    symbols_serializer.is_valid(raise_exception=True)
    symbols_serializer.save()
    # TODO(Nikola): Skip already saved symbols and mention in response?
    return JsonResponse(symbols_serializer.data, status=201, safe=False)
