from oscar.core.loading import get_model
from rest_framework import serializers


class StockRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_model('partner', 'StockRecord')
        fields = ["price_excl_tax"]

class MessageSerializer(serializers.ModelSerializer):
    price_excl_tax = StockRecordSerializer(read_only=True)

    class Meta:
        model = get_model('catalogue', 'Product')
        fields = ['title', 'description']
