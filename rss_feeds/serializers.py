from rest_framework import serializers
from .models import News, Symbols


def symbol_name_validator(name):
    if not isinstance(name, str):
        raise serializers.ValidationError("Symbol name must be a string!")
    elif name.upper() != name:
        raise serializers.ValidationError("Symbol name must be uppercase!")


def simple_string_validator(value):
    if not isinstance(value, str):
        raise serializers.ValidationError("Must be a string!")


class SymbolsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[symbol_name_validator])

    def create(self, validated_data):
        try:
            symbol = Symbols.objects.get(name=validated_data['name'])
            symbol.enabled = validated_data['enabled']
            symbol.save()
        except Symbols.DoesNotExist:
            symbol = Symbols.objects.create(**validated_data)
        return symbol

    class Meta:
        model = Symbols
        fields = ('name', 'enabled')


class NewsSerializer(serializers.ModelSerializer):
    guid = serializers.CharField(validators=[simple_string_validator])

    def create(self, validated_data):
        try:
            news = News.objects.get(guid=validated_data['guid'])
            news.title = validated_data['title']
            news.description = validated_data['description']
            news.link = validated_data['link']
            news.published_on = validated_data['published_on']
            news.save()
        except News.DoesNotExist:
            news = News.objects.create(**validated_data)
        return news

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
