# Generated by Django 2.2.4 on 2019-10-01 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0017_product_production_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='media_group_id',
            field=models.CharField(blank=True, db_index=True, default='', max_length=50),
        ),
    ]
