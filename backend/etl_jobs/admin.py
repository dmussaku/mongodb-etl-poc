from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from .models import Pipeline, JobExecution
from .tasks import run_pipeline_task


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("name", "load_type", "is_enabled", "is_active", "run_pipeline_button", "created_at")
    list_filter = ("load_type", "is_enabled", "is_active", "created_at")
    search_fields = ("name", "description", "source_table", "destination_table")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Basic Information", {"fields": ("name", "description", "is_active")}),
        ("Source Configuration", {"fields": ("source_uri", "source_database", "source_table", "source_aggregation_query")}),
        (
            "Destination Configuration",
            {"fields": ("destination_uri", "destination_database", "destination_table")},
        ),
        (
            "Load Configuration",
            {
                "fields": (
                    "load_type",
                    "incremental_strategy",
                    "incremental_key",
                    "primary_key",
                )
            },
        ),
        ("Masking Configuration", {"fields": ("masking_config",)}),
        ("Scheduling", {"fields": ("frequency", "is_enabled")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        return [
            path('<int:pipeline_id>/run/', self.admin_site.admin_view(self.run_pipeline), name='run_pipeline'),
        ] + urls

    def run_pipeline_button(self, obj):
        return format_html('<a class="button" href="{}">Run</a>', reverse('admin:run_pipeline', args=[obj.pk]))
    run_pipeline_button.short_description = "Action"

    def run_pipeline(self, request, pipeline_id):
        run_pipeline_task.delay(pipeline_id)
        messages.success(request, "Pipeline scheduled!")
        return HttpResponseRedirect(reverse('admin:etl_jobs_pipeline_changelist'))


@admin.register(JobExecution)
class JobExecutionAdmin(admin.ModelAdmin):
    list_display = (
        "pipeline",
        "status",
        "started_at",
        "duration_seconds",
        "rows_processed",
        "created_at",
    )
    list_filter = ("status", "created_at", "pipeline")
    search_fields = ("pipeline__name", "execution_id", "error_message")
    readonly_fields = ("created_at", "started_at", "completed_at")
    date_hierarchy = "created_at"

    fieldsets = (
        ("Pipeline Information", {"fields": ("pipeline", "status", "execution_id")}),
        ("Timing", {"fields": ("started_at", "completed_at", "duration_seconds")}),
        (
            "Metrics",
            {
                "fields": (
                    "rows_processed",
                    "rows_inserted",
                    "rows_updated",
                    "rows_failed",
                )
            },
        ),
        ("Output", {"fields": ("logs", "error_message"), "classes": ("collapse",)}),
        ("Record Information", {"fields": ("created_at",), "classes": ("collapse",)}),
    )
