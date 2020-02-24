from django.db import models
from oscar.apps.catalogue.abstract_models import AbstractProduct


class Product(AbstractProduct):
    production_days = models.IntegerField(blank=True, null=True)
    media_group_id = models.CharField(blank=True, default="", max_length=50, db_index=True)
    message_id = models.IntegerField(db_index=True, null=True)


from oscar.apps.catalogue.models import *
