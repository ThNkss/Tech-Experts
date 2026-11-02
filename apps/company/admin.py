from django.contrib import admin
from .models import CompanyProfile

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ('English / primary content', {'fields': ('name', 'tagline', 'introduction', 'capabilities', 'address')}),
        ('Persian translation (optional)', {'fields': ('name_fa', 'tagline_fa', 'introduction_fa', 'capabilities_fa', 'address_fa'), 'classes': ('collapse',)}),
        ('Contact details', {'fields': ('email', 'phone')}),
    )

    def has_add_permission(self, request):
        return not CompanyProfile.objects.exists()
