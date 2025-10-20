from django.contrib import admin
from .models import Batch

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("batch_name", "start_date", "end_date", "created_by", "slug")
    search_fields = ("batch_name", "slug", "description", "created_by__email")
    list_filter = ("start_date", "end_date", "created_by")
    ordering = ("-start_date",)
    readonly_fields = ("slug",)

    def get_exclude(self, request, obj=None):
        return ['created_by']

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        obj.save()
