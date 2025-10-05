from django.contrib import admin
from .models import Batch

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("batch_name", "start_date", "end_date",  "created_by")
    search_fields = ("batch_name", "batch_code", "description", "created_by__username", )
    list_filter = ("start_date", "end_date", "created_by")
    ordering = ("-created_by",)
# Register your models here.
