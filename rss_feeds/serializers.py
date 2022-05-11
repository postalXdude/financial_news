from rest_framework import serializers
from .models import News, Symbols


class SymbolsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symbols
        fields = ('name',)


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = (
            'guid',
            'title',
            'description',
            'link',
            'published_on',
            'symbol'
        )
