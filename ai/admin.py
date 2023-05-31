from django.contrib import admin
from ai.models import TokenUsage


class TokenUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'tokens_used')
    search_fields = ('user__username',)
    list_filter = ('date',)
    ordering = ('-date',)


admin.site.register(TokenUsage, TokenUsageAdmin)
