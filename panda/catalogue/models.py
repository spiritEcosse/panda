from django.db import models
from oscar.apps.catalogue.abstract_models import AbstractProduct


class Product(AbstractProduct):
    production_days = models.IntegerField(blank=True, null=True)


from oscar.apps.catalogue.models import *
