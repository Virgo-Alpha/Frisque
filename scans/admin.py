from django.contrib import admin
from .models import ScanJob, ScanResult

@admin.register(ScanJob)
class ScanJobAdmin(admin.ModelAdmin):
    """
    Customizes the display of ScanJob records in the Django admin.
    """
    list_display = ('company_name', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'user')
    search_fields = ('company_name', 'user__email', 'id__hex')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('company_name', 'company_url', 'user', 'status')
        }),
        ('Output', {
            'fields': ('final_report',),
            'classes': ('collapse',) # Makes this section collapsible
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    """
    Customizes the display of ScanResult records in the Django admin.
    """
    list_display = ('job', 'agent_name', 'status', 'created_at')
    list_filter = ('agent_name', 'status')
    search_fields = ('job__company_name', 'job__id__hex')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('job', 'agent_name', 'status')
        }),
        ('Output', {
            'fields': ('raw_output', 'error_message'),
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )