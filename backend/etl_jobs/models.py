from django.db import models
from django.contrib.postgres.fields import ArrayField


class Pipeline(models.Model):
    """ETL Pipeline configuration."""

    LOAD_TYPE_CHOICES = (
        ("full", "Full Load"),
        ("incremental", "Incremental"),
    )

    INCREMENTAL_STRATEGY_CHOICES = (
        ("append", "Append"),
        ("merge", "Merge"),
        ("replace", "Replace"),
        ("upsert", "Upsert"),
    )

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    # Source Configuration
    source_uri = models.TextField()
    source_database = models.CharField(max_length=255, blank=True, null=True)
    source_table = models.CharField(max_length=255)
    source_aggregation_query = ArrayField(
        base_field=models.JSONField(),
        blank=True,
        null=True,
        help_text="Aggregation pipeline as a list of MongoDB aggregation stages",
    )

    # Destination Configuration
    destination_uri = models.TextField()
    destination_database= models.CharField(max_length=255, blank=True, null=True)
    destination_table = models.CharField(max_length=255)

    # Load Configuration
    load_type = models.CharField(
        max_length=50, choices=LOAD_TYPE_CHOICES, default="full"
    )
    incremental_strategy = models.CharField(
        max_length=50, choices=INCREMENTAL_STRATEGY_CHOICES, blank=True, null=True
    )
    incremental_key = models.CharField(max_length=255, blank=True, null=True)
    primary_key = models.CharField(max_length=255, blank=True, null=True)

    # Masking (stored as JSON)
    masking_config = models.JSONField(
        default=dict, blank=True, help_text="Masking rules as key-value pairs"
    )

    # Scheduling
    frequency = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Cron expression (e.g., '0 2 * * *')",
    )
    is_enabled = models.BooleanField(default=True)

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}"


class JobExecution(models.Model):
    """Tracks each pipeline execution."""

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("running", "Running"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    )

    pipeline = models.ForeignKey(
        Pipeline, on_delete=models.CASCADE, related_name="executions"
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )

    # Metrics
    rows_processed = models.BigIntegerField(null=True, blank=True)
    rows_inserted = models.BigIntegerField(null=True, blank=True)
    rows_updated = models.BigIntegerField(null=True, blank=True)
    rows_failed = models.BigIntegerField(null=True, blank=True)

    # Logs
    logs = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    execution_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.pipeline.name} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
