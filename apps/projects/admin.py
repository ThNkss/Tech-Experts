from django.contrib import admin
from .models import Project, ProjectProduct, ProjectMedia, Industry, ProjectParty

class ProductInline(admin.TabularInline):
    model = ProjectProduct
    autocomplete_fields = ('product',)
    extra = 0

class MediaInline(admin.TabularInline):
    model = ProjectMedia
    autocomplete_fields = ('asset',)
    extra = 0

class PartyInline(admin.StackedInline):
    model = ProjectParty
    autocomplete_fields = ('organization',)
    extra = 0

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'status', 'progress_percent', 'published', 'publication_authorized')
    list_filter = ('published', 'status', 'industry', 'publication_authorized')
    search_fields = ('title', 'customer__name')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('customer', 'cover')
    fieldsets = (
        ('Publishing', {'fields': ('slug', 'published', 'publication_authorized', 'featured', 'cover')}),
        ('Project records (internal customer identity)', {'fields': ('customer', 'industry', 'status', 'progress_percent', 'start_date', 'completion_date')}),
        ('Optional project value', {'fields': ('contract_value', 'currency', 'show_contract_value')}),
        ('English / primary public content', {'fields': ('title', 'public_customer_name', 'summary', 'description', 'challenges', 'solution', 'location')}),
        ('Persian translation (optional)', {'fields': ('title_fa', 'public_customer_name_fa', 'summary_fa', 'description_fa', 'challenges_fa', 'solution_fa', 'location_fa'), 'classes': ('collapse',)}),
    )
    inlines = (PartyInline, ProductInline, MediaInline)

@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
