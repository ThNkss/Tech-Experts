from django.contrib import admin
from .models import CustomerOrganization

@admin.register(CustomerOrganization)
class CustomerOrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'contact_phone')
    search_fields = ('name', 'national_id')
