from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


CustomUser = get_user_model()


class TokenUsage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    tokens_used = models.IntegerField(default=0)


class Conversation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Message(models.Model):
    SENDER_USER = 'user'
    SENDER_AI = 'ai'
    SENDER_CHOICES = [
        (SENDER_USER, 'User'),
        (SENDER_AI, 'AI'),
    ]

    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

