from django.contrib import admin

from .models import MediaItem


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "media_type", "is_featured", "uploaded_by", "created_at")
    list_filter = ("category", "media_type", "is_featured")
    search_fields = ("title", "description")
    readonly_fields = ("media_type", "created_at")
