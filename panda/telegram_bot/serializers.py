import re
from decimal import Decimal, InvalidOperation

from oscar.core.loading import get_model
from rest_framework import serializers


class StockRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_model('partner', 'StockRecord')
        fields = ["price_excl_tax"]


class MessageSerializer(serializers.ModelSerializer):
    price_excl_tax = StockRecordSerializer(read_only=True, many=False)
    category_str = serializers.CharField(required=True)
    production_days = serializers.IntegerField(required=False)
    product_class = serializers.CharField(required=False)

    class Meta:
        model = get_model('catalogue', 'Product')
        fields = ['title', 'description', 'price_excl_tax', "category_str", "product_class"]
        extra_kwargs = {
            'title': {'required': True},
            'description': {'required': True},
            'price_excl_tax': {'required': True},
        }

    def validate(self, data):
        if not data['product_class']:
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
