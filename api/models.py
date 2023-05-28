from django.db import models
from django.db.models.aggregates import Count
from random import randint

class Author(models.Model):
    name = models.CharField(max_length=100, default=None)
    photo = models.ImageField(upload_to='pics', default=None, blank=True)
    description = models.TextField(blank=True, null=False)

    def __str__(self):
        return self.name

class StihManager(models.Manager):
    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count -1 )
        return self.all()[random_index]

class Stih(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE,  default=None)
    title = models.CharField("Stih title", max_length=1000, blank=True)
    epigraph =  models.CharField("Epigraph", max_length=1000, blank=True)
    body = models.TextField(blank=True, null=True)
    createdAt = models.CharField("Created At", max_length=255, blank=True)
    objects = StihManager()


    def __str__(self):
        return self.title

