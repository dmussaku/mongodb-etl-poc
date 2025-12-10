from django.contrib import admin
from .models import Pipeline, JobExecution


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('name', 'load_type', 'is_enabled', 'is_active', 'created_at')
    list_filter = ('load_type', 'is_enabled', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'source_table', 'destination_table')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Source Configuration', {
            'fields': ('source_uri', 'source_table')
        }),
        ('Destination Configuration', {
            'fields': ('destination_uri', 'destination_table')
        }),
        ('Load Configuration', {
            'fields': ('load_type', 'incremental_strategy', 'incremental_key', 'primary_key')
        }),
        ('Masking Configuration', {
            'fields': ('masking_config',)
        }),
        ('Scheduling', {
            'fields': ('frequency', 'is_enabled')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JobExecution)
class JobExecutionAdmin(admin.ModelAdmin):
    list_display = ('pipeline', 'status', 'started_at', 'duration_seconds', 'rows_processed', 'created_at')
    list_filter = ('status', 'created_at', 'pipeline')
    search_fields = ('pipeline__name', 'execution_id', 'error_message')
    readonly_fields = ('created_at', 'started_at', 'completed_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Pipeline Information', {
            'fields': ('pipeline', 'status', 'execution_id')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration_seconds')
        }),
        ('Metrics', {
            'fields': ('rows_processed', 'rows_inserted', 'rows_updated', 'rows_failed')
        }),
        ('Output', {
            'fields': ('logs', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Record Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
