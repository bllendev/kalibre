# Generated by Django 4.2 on 2023-05-09 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0014_book__title_lemmatized'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='json_links',
            field=models.JSONField(null=True),
        ),
    ]