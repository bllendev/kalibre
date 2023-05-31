from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


CustomUser = get_user_model()


class TokenUsage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    tokens_used = models.IntegerField(default=0)
