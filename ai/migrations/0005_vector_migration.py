from pgvector.django import VectorExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0004_alter_conversation_user'),
    ]

    operations = [
        VectorExtension(),
    ]
