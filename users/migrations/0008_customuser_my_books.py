# Generated by Django 4.2 on 2023-10-06 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0015_alter_book_json_links'),
        ('users', '0007_alter_email_translate_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='my_books',
            field=models.ManyToManyField(to='books.book'),
        ),
    ]