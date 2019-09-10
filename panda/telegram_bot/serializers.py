import datetime
import re

from oscar.core.loading import get_classes
from oscar.core.loading import get_model
from rest_framework import serializers

Partner, StockRecord = get_classes('partner.models', ['Partner',
                                                      'StockRecord'])
ProductClass, Product, Category, ProductCategory = get_classes(
    'catalogue.models', ('ProductClass', 'Product', 'Category',
                         'ProductCategory'))

class ProductClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductClass
        fields = ["name"]


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ["name"]


class StockRecordSerializer(serializers.ModelSerializer):
    partner = PartnerSerializer(many=False, required=False)

    class Meta:
        model = StockRecord
        fields = ["partner_sku", "price_excl_tax", "num_in_stock", "partner"]
        extra_kwargs = {
            "num_in_stock": {"default": 1},
        }


class MessageSerializer(serializers.ModelSerializer):
    availability = serializers.BooleanField()
    stock = StockRecordSerializer(many=False, source="product")
    category_str = serializers.CharField()
    production_days = serializers.IntegerField(required=False)
    product_class = ProductClassSerializer(many=False)
    upc = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ['title', "availability", 'stock', 'description', "category_str",
                  "production_days", "product_class", "upc"]
        extra_kwargs = {
            'title': {'required': True},
            'availability': {'required': True},
            'stock': {'required': True},
            'description': {'required': True},
            'category_str': {'required': True},
        }

    def parse_upc(self, *args):
        now = datetime.datetime.now()
        return int((now - datetime.datetime(1970, 1, 1)).total_seconds() * 1000000)

    def to_internal_value(self, data):
        for field in self.fields.values():
            #ToDo replace on https://www.django-rest-framework.org/api-guide/validators/#class-based
            parse_method = getattr(self, 'parse_' + field.field_name, None)

            if parse_method:
                if field.field_name in data:
                    data[field.field_name] = parse_method(data[field.field_name])
                elif field.required:
                    data[field.field_name] = parse_method()

        data['product_class']['name'] = data['category_str'].split(">")[0].strip() + " partner"
        data['stock']['partner'] = {}
        data['stock']['partner']['name'] = data['product_class']['name']
        data['stock']['partner_sku'] = data['upc']

        if not data["availability"]:
            data['stock']['num_in_stock'] = 0
        return super().to_internal_value(data)

    def parse_availability(self, value):
        return True if value in ["В наличии", "На заказ"] else False

    def parse_production_days(self, value):
        match = re.match(r".*:\s*(?P<days>\d+)(.*)*", value)

        try:
            days = match.group("days")
        except AttributeError:
            return ""

        return int(days)

    def parse_category_str(self, value):
        separator = '>'
        return " > ".join(map(lambda el: el.strip().capitalize(), value.split(separator)))

    def parse_stock(self, value):
        match = re.match(r".*:\s*(?P<price>\d+)(?P<hundredths>\.\d+)*(.*/.*)*", value)

        try:
            hundredths = match.group("hundredths") or ""
            price = match.group("price") + hundredths
        except AttributeError:
            price = ""

        return {"stock": price}

    def parse_product_class(self):
        return {"product_class": ""}
