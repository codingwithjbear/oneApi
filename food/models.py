from django.db import models

# Create your models here.

class Search(models.Model):
    term = models.CharField(max_length=200)
    count = models.IntegerField(default=1)
