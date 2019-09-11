import datetime
import re

from oscar.core.loading import get_classes
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
        extra_kwargs = {
            'name': {'required': True},
        }

    def __init__(self, *args, **kwargs):
        self.parsed_data = kwargs.get('data', {})
        super().__init__(*args, **kwargs)

    def parser(self):
        data = {}
        for field in self.fields.values():
            if field.required:
                initial = getattr(self, 'initial_' + field.field_name, None)

                if initial:
                    data[field.field_name] = initial()
        return data

    def initial_name(self):
        return self.parsed_data['stock']['partner']['name'].split(" partner")[0]


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ["name"]
        extra_kwargs = {
            'name': {'required': True},
        }

    def __init__(self, *args, **kwargs):
        self.parsed_data = kwargs.get('data', {})
        super().__init__(*args, **kwargs)

    def parser(self):
        data = {}
        for field in self.fields.values():
            if field.required:
                initial = getattr(self, 'initial_' + field.field_name, None)

                if initial:
                    data[field.field_name] = initial()
        return data

    def initial_name(self):
        return self.parsed_data['category_str'].split(">")[0].strip().capitalize() + " partner"


class StockRecordSerializer(serializers.ModelSerializer):
    partner = PartnerSerializer(many=False)

    class Meta:
        model = StockRecord
        fields = ["partner_sku", "price_excl_tax", "num_in_stock", "partner"]
        extra_kwargs = {
            'num_in_stock': {'required': True},
            'partner_sku': {'required': True},
            'price_excl_tax': {'required': True},
        }

    def __init__(self, *args, **kwargs):
        self.parsed_data = kwargs.get('data', {})
        super().__init__(*args, **kwargs)

    def parser(self, value):
        data = {}
        for field in self.fields.values():
            #ToDo replace on https://www.django-rest-framework.org/api-guide/validators/#class-based
            parse_method = getattr(self, 'parse_' + field.field_name, None)
            field.parsed_data = self.parsed_data

            if parse_method:
                data[field.field_name] = parse_method(field, value)
            elif field.required:
                initial = getattr(self, 'initial_' + field.field_name, None)

                if initial:
                    data[field.field_name] = initial(field)
        return data

    def initial_partner_sku(self, _):
        now = datetime.datetime.now()
        return int((now - datetime.datetime(1970, 1, 1)).total_seconds() * 1000000)

    def initial_num_in_stock(self, _):
        return int(self.parsed_data["availability"])

    def initial_partner(self, field):
        return field.parser()

    def parse_price_excl_tax(self, _, value):
        match = re.match(r".*:\s*(?P<price>\d+)(?P<hundredths>\.\d+)*(.*/.*)*", value)

        try:
            hundredths = match.group("hundredths") or ""
            price = match.group("price") + hundredths
        except AttributeError:
            price = ""

        return price


class MessageSerializer(serializers.ModelSerializer):
    availability = serializers.BooleanField()
    stock = StockRecordSerializer(many=False, source="product")
    category_str = serializers.CharField()
    production_days = serializers.IntegerField(required=False)
    product_class = ProductClassSerializer(many=False)

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
            'upc': {'required': True},
        }

    def __init__(self, *args, **kwargs):
        self.parsed_data = kwargs.get('data', {})
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        for field in self.fields.values():
            #ToDo replace on https://www.django-rest-framework.org/api-guide/validators/#class-based
            parse_method = getattr(self, 'parse_' + field.field_name, None)
            field.parsed_data = self.parsed_data

            if field.field_name in data:
                if parse_method:
                    data[field.field_name] = parse_method(field, data[field.field_name])
            elif field.required:
                initial = getattr(self, 'initial_' + field.field_name, None)

                if initial:
                    data[field.field_name] = initial(field)

        return super().to_internal_value(data)

    def initial_upc(self, *args):
        return self.parsed_data['stock']['partner_sku']

    def parse_availability(self, field, value):
        data = True if value in ["В наличии", "На заказ"] else False
        self.parsed_data.update({field.field_name: data})
        return data

    def parse_production_days(self, _, value):
        match = re.match(r".*:\s*(?P<days>\d+)(.*)*", value)

        try:
            days = match.group("days")
        except AttributeError:
            return ""

        return int(days)

    def parse_category_str(self, _, value):
        separator = '>'
        return " > ".join(map(lambda el: el.strip().capitalize(), value.split(separator)))

    def parse_stock(self, field, value):
        data = field.parser(value)
        self.parsed_data.update({field.field_name: data})
        return data

    def initial_product_class(self, field):
        return field.parser()
