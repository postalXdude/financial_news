from rest_framework import serializers
from .models import News, Symbols


class SymbolsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symbols
        fields = ('name', 'enabled')

    def create(self, validated_data):
        try:
            symbol = Symbols.objects.get(name=validated_data['name'])
            symbol.enabled = validated_data['enabled']
            symbol.save()
        except Symbols.DoesNotExist:
            Symbols.objects.create(**validated_data)


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

    def create(self, validated_data):
        try:
            news = News.objects.get(name=validated_data['guid'])
            news.title = validated_data['title']
            news.description = validated_data['description']
            news.link = validated_data['link']
            news.published_on = validated_data['published_on']
            news.save()
        except Symbols.DoesNotExist:
            News.objects.create(**validated_data)
