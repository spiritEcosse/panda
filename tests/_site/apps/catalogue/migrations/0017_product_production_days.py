# Generated by Django 2.2.4 on 2019-09-17 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0016_auto_20190327_0757'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='production_days',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
