from django.contrib import admin
from ai.models import TokenUsage, Conversation, Message


# extra admin views
class MessageInline(admin.TabularInline):  # or admin.StackedInline if you prefer a vertical layout
    model = Message
    extra = 1  # determines how many empty forms are displayed in the admin
    readonly_fields = ('sender', 'text', 'sent_at')  # these fields will be displayed but not editable
    can_delete = False  


# admin models
@admin.register(TokenUsage)
class TokenUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'tokens_used')
    search_fields = ('user__username',)
    list_filter = ('date',)
    ordering = ('-date',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'started_at', 'last_updated')
    search_fields = ('id', 'user__username',)  # assuming `username` is a field on CustomUser
    list_filter = ('started_at', 'last_updated', 'user')
    inlines = [MessageInline]  # this adds the inline form for messages



@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'text', 'sent_at')
    search_fields = ('id', 'conversation__id', 'text')
    list_filter = ('sent_at', 'sender', 'conversation__user')