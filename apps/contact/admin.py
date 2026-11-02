from django.contrib import admin
from .models import Inquiry

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'kind', 'product', 'handled', 'created_at')
    list_filter = ('handled', 'kind', 'created_at')
    search_fields = ('name', 'email', 'organization')
    readonly_fields = ('created_at', 'updated_at')
