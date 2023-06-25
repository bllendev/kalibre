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

    def get_messages(self):
        unorganized_messages = self.messages.all().order_by('sent_at')
        organized_messages = []
        for idx, msg in enumerate(unorganized_messages):
            if idx == 0:  # system prompt
                organized_messages.append(msg.get_message(message_str=msg.text, role="system"))
            organized_messages.append(msg.get_message(message_str=msg.text, role=msg.sender))
        return organized_messages


class Message(models.Model):
    SENDER_USER = 'user'
    SENDER_AI = 'ai'
    SENDER_CHOICES = [
        (SENDER_USER, 'User'),
        (SENDER_AI, 'AI'),
    ]

    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.CharField(default="", max_length=5000)
    sent_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_message(message_str, role):
        if role == "ai":
            role = "assistant"
        return {"role": role, "content": message_str}
