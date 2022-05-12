import json
import logging

from django.http import JsonResponse
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from rest_framework.decorators import api_view, parser_classes
from rest_framework import generics
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import NotFound

from .models import Symbols, News
from .serializers import NewsSerializer, SymbolsSerializer

logger = logging.getLogger(__name__)


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
        return NotFound(f'Symbol `{symbol}` does not exists!')
    return JsonResponse(news, status=200, safe=False)


@api_view(['POST'])
@parser_classes([JSONParser])
def store_symbols(request):
    """
    Store new symbols that will be used for fetching Yahoo RSS feeds.
    """
    symbols_serializer = SymbolsSerializer(data=request.data, many=True)
    symbols_serializer.is_valid(raise_exception=True)
    symbols_serializer.save()
    return JsonResponse(symbols_serializer.data, status=201, safe=False)


@api_view(['POST'])
@parser_classes([JSONParser])
def trigger_periodic_tasks(request):
    """
    Periodic tasks are triggered for each enabled symbol.
    """
    enabled = []
    disabled = []
    schedule, _ = IntervalSchedule.objects.get_or_create(**request.data)
    for symbol in Symbols.objects.all():
        periodic_task_name = f'{symbol.name}_periodic_sync'
        periodic_task, _ = PeriodicTask.objects.get_or_create(
            interval=schedule,
            name=periodic_task_name,
            task='rss_feeds.tasks.fetch_rss_from_source_for_symbol',
            args=json.dumps([symbol.name])
        )
        if symbol.enabled:
            periodic_task.enabled = True
            enabled.append(periodic_task_name)
        else:
            periodic_task.enabled = False
            disabled.append(periodic_task_name)
        periodic_task.save()
    response = {'enabled': enabled, 'disabled': disabled}
    return JsonResponse(response, status=201, safe=False)
