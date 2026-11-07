from django.contrib import admin

from .models import ActivityHistory, VirtualAgent, VirtualService


class VirtualServiceInline(admin.TabularInline):
    model = VirtualService
    extra = 0


class ActivityHistoryInline(admin.TabularInline):
    model = ActivityHistory
    fields = ('action', 'summary', 'created_at')
    readonly_fields = fields
    extra = 0
    can_delete = False


@admin.register(VirtualAgent)
class VirtualAgentAdmin(admin.ModelAdmin):
    list_display = ('persona_label', 'user', 'role', 'is_enabled', 'last_simulated_at')
    list_filter = ('role', 'is_enabled')
    search_fields = ('persona_label', 'user__username', 'user__phone_number')
    readonly_fields = ('created_at', 'last_simulated_at')
    inlines = (VirtualServiceInline, ActivityHistoryInline)


@admin.register(VirtualService)
class VirtualServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'agent', 'price', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name', 'agent__persona_label', 'agent__user__username')


@admin.register(ActivityHistory)
class ActivityHistoryAdmin(admin.ModelAdmin):
    list_display = ('agent', 'action', 'summary', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('agent__persona_label', 'agent__user__username', 'summary')
    readonly_fields = ('agent', 'event_key', 'action', 'summary', 'metadata', 'created_at')
