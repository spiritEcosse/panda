import datetime
import os
import re

from PIL import Image
from django.conf import settings
from django.core.files import File
from oscar.core.loading import get_classes, get_class
from rest_framework import serializers

Partner, StockRecord = get_classes('partner.models', ['Partner',
                                                      'StockRecord'])
ProductClass, Product, ProductCategory, ProductImage = get_classes(
    'catalogue.models', ('ProductClass', 'Product', 'ProductCategory', "ProductImage"))
create_from_breadcrumbs = get_class('catalogue.categories', 'create_from_breadcrumbs')


class CommonSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        self.parsed_data = kwargs.get('data', {})
        super().__init__(*args, **kwargs)

    def parser(self, data):
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
        return data


class ProductImageSerializer(CommonSerializer):
    class Meta:
        model = ProductImage
        fields = ('original', )

    def parse_original(self, _, value):
        file_path = settings.TELEGRAM_FORMAT_IMAGE_FILE.format(
            self.parsed_data['stock']['partner_sku']
        )

        if value.download(file_path):
            trial_image = Image.open(file_path)
            trial_image.verify()
            return File(open(file_path, 'rb'))

    def create(self, validated_data, product=None):
        original = validated_data.pop('original')
        im = self.Meta.model(product=product, **validated_data)
        file_name = original.name.split('/')[-1]
        im.original.save(file_name, original, save=False)
        im.save()

        if not settings.TELEGRAM_HOLD_IMAGE_FILE:
            os.remove(original.name)


class ProductClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductClass
        fields = ["name"]

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

    def create(self, validated_data):
        return self.Meta.model.objects.get_or_create(**validated_data)[0]


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

    def create(self, validated_data):
        return self.Meta.model.objects.get_or_create(**validated_data)[0]


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

    def create(self, validated_data, product=None):
        partner = self.fields['partner'].create(
            validated_data.pop('partner')
        )
        return self.Meta.model.objects.create(
            product=product, partner=partner, **validated_data
        )


class MessageSerializer(CommonSerializer):
    availability = serializers.BooleanField()
    stock = StockRecordSerializer(many=False)
    category_str = serializers.CharField()
    product_class = ProductClassSerializer(many=False)
    image = ProductImageSerializer(many=False, required=True)

    class Meta:
        model = Product
        fields = ['title', "availability", 'stock', 'description', "category_str",
                  "production_days", "product_class", "upc", "image", "media_group_id"]
        extra_kwargs = {
            'title': {'required': True},
            'availability': {'required': True},
            'stock': {'required': True},
            'description': {'required': True},
            'category_str': {'required': True},
            'upc': {'required': True},
        }

    def to_internal_value(self, data):
        return super().to_internal_value(self.parser(data))

    def initial_upc(self, *args):
        return self.parsed_data['stock']['partner_sku']

    def parse_availability(self, field, value):
        data = True if value in ["В наличии", "На заказ"] else False
        self.parsed_data.update({field.field_name: data})
        return data

    def parse_production_days(self, _, value):
        match = re.match(r".*:\s*(?P<days>\d+)(.*)*", value)

        try:
            days = int(match.group("days"))
        except AttributeError:
            days = None

        return days

    def parse_category_str(self, _, value):
        separator = '>'
        return " > ".join(map(lambda el: el.strip().capitalize(), value.split(separator)))

    def parse_stock(self, field, value):
        data = field.parser(value)
        self.parsed_data.update({field.field_name: data})
        return data

    def initial_product_class(self, field):
        return field.parser()

    def parse_image(self, field, value):
        return field.parser(value)

    def create(self, validated_data):
        validated_data.pop('availability')
        stock_data = validated_data.pop('stock')
        image = validated_data.pop('image')
        product_class = self.fields['product_class'].create(
            validated_data.pop('product_class')
        )
        cat = create_from_breadcrumbs(validated_data.pop('category_str'))
        item = self.Meta.model.objects.create(product_class=product_class, **validated_data)
        ProductCategory.objects.create(product=item, category=cat)
        self.fields['stock'].create(stock_data, product=item)
        self.fields['image'].create(image, product=item)
        return item

