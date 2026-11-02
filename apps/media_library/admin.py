from django.contrib import admin
from .models import MediaAsset

@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'uploaded_by')
    search_fields = ('title', 'alt_text')
    readonly_fields = ('uploaded_by',)

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
