from django.db import models


class Symbols(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class News(models.Model):
    guid = models.CharField(max_length=50, primary_key=True)
    title = models.TextField()
    description = models.TextField()
    link = models.TextField()
    published_on = models.DateTimeField()
    saved_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    symbol = models.ForeignKey(
        Symbols,
        on_delete=models.CASCADE,
        related_name='News'
    )
