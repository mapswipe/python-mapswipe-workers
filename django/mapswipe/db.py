from django.db import models
from django_cte import CTEManager


class Model(models.Model):
    cte_objects = CTEManager()
    objects = models.Manager()

    class Meta:
        abstract = True
