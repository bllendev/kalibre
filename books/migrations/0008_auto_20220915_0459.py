# Generated by Django 2.2.7 on 2022-09-15 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_book_filetype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
    ]
