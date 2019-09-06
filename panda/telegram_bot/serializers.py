import re
from decimal import Decimal, InvalidOperation
import datetime
from oscar.core.loading import get_model
from rest_framework import serializers


class StockRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_model('partner', 'StockRecord')
        fields = ["price_excl_tax", "num_in_stock"]


class MessageSerializer(serializers.ModelSerializer):
    availability = serializers.BooleanField()
    price_excl_tax = StockRecordSerializer(read_only=True, many=False)
    category_str = serializers.CharField()
    production_days = serializers.IntegerField()
    product_class = serializers.CharField()
    upc = serializers.IntegerField()

    class Meta:
        model = get_model('catalogue', 'Product')
        fields = ['title', "availability", 'price_excl_tax', 'description', "category_str",
                  "production_days", "product_class", "upc"]
        extra_kwargs = {
            'title': {'required': True},
            'availability': {'required': True},
            'price_excl_tax': {'required': True},
            'description': {'required': True},
            'category_str': {'required': True},
            'production_days': {'required': False},
            'product_class': {'required': False},
            'upc': {'required': False},
        }

    def get_upc(self, *args):
        now = datetime.datetime.now()
        return int((now - datetime.datetime(1970, 1, 1)).total_seconds() * 1000000)

    def validate_availability(self, value):
        return True if value == "В наличии" else False

    def validate(self, data):
        if not data.get('production_days', False):
            raise serializers.ValidationError("")
        return data

    def validate_production_days(self, value):
        match = re.match(r".*:\s*(?P<days>\d+)(.*)*", value)

        try:
            days = match.group("days")
        except AttributeError:
            raise serializers.ValidationError("Wrong field production_days.")

        return int(days)

    def validate_category_str(self, value):
        separator = '>'
        return " > ".join(map(lambda el: el.strip().capitalize(), value.split(separator)))

    def validate_price_excl_tax(self, value):
        match = re.match(r".*:\s*(?P<price>\d+)(?P<hundredths>\.\d+)*(.*/.*)*", value)

        try:
            hundredths = match.group("hundredths") or ""
            price = match.group("price") + hundredths
        except AttributeError:
            raise serializers.ValidationError("Wrong field price.")

        try:
            return Decimal(price)
        except InvalidOperation:
            raise serializers.ValidationError("Wrong field price.")
