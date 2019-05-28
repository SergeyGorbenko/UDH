from django.db import models


class Object(models.Model):
    lat = models.FloatField()
    lng = models.FloatField()
    symbolCode = models.TextField()
    create = models.DateTimeField(auto_now_add=True)
    modify = models.DateTimeField(auto_now=True)
