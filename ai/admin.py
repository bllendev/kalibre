from django.contrib import admin
from ai.models import TokenUsage, Conversation, Message


class TokenUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'tokens_used')
    search_fields = ('user__username',)
    list_filter = ('date',)
    ordering = ('-date',)


admin.site.register(TokenUsage, TokenUsageAdmin)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'started_at', 'last_updated')
    search_fields = ('id', 'user__username',)  # assuming `username` is a field on CustomUser
    list_filter = ('started_at', 'last_updated', 'user')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'text', 'sent_at')
    search_fields = ('id', 'conversation__id', 'text')
    list_filter = ('sent_at', 'sender', 'conversation__user')