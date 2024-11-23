from django.contrib import admin
from ai.models import (
    TokenUsage,
    Conversation,
    VectorSearch,
    Message,
)

# extra admin views
# or admin.StackedInline if you prefer a vertical layout


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1  # determines how many empty forms are displayed in the admin
    # these fields will be displayed but not editable
    readonly_fields = ("sender", "text", "sent_at")
    can_delete = False


# admin models
@admin.register(TokenUsage)
class TokenUsageAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "tokens_used")
    search_fields = ("user__username",)
    list_filter = ("date",)
    ordering = ("-date",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "started_at", "last_updated")
    # assuming `username` is a field on CustomUser
    search_fields = (
        "id",
        "user__username",
    )
    list_filter = ("started_at", "last_updated", "user")
    inlines = [MessageInline]  # this adds the inline form for messages


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "text", "sent_at")
    search_fields = ("id", "conversation__id", "text")


@admin.register(VectorSearch)
class VectorSearchAdmin(admin.ModelAdmin):
    # List the fields you want to display in the admin list view.
    list_display = ("id", "created_at", "updated_at")

    # Search fields allow search by these fields.
    search_fields = ("metadata",)
