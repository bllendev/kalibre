# Generated by Django 2.2.7 on 2022-11-13 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0008_auto_20220915_0459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='link',
            field=models.CharField(default='', max_length=562),
        ),
    ]
