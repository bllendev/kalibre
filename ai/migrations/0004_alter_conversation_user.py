# Generated by Django 4.2 on 2023-10-07 03:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ai', '0003_alter_message_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations', to=settings.AUTH_USER_MODEL),
        ),
    ]
