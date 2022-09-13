from django.db import models


class ArrayLength(models.Func):
    function = 'CARDINALITY'
