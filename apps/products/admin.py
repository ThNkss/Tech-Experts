from django.contrib import admin
from .models import Product, ProductCategory, ProductFeature, ProductSpecification, ProductMedia, ProductSection, ProductFAQ

class FeatureInline(admin.StackedInline):
    model = ProductFeature
    extra = 0
    autocomplete_fields = ('image',)

class SpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 0

class MediaInline(admin.TabularInline):
    model = ProductMedia
    autocomplete_fields = ('asset',)
    extra = 0

class SectionInline(admin.StackedInline):
    model = ProductSection
    autocomplete_fields = ('image',)
    extra = 0

class FAQInline(admin.StackedInline):
    model = ProductFAQ
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'published', 'featured')
    list_filter = ('published', 'featured', 'category', 'status')
    search_fields = ('name', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('cover',)
    fieldsets = (
        ('Publishing', {'fields': ('slug', 'category', 'cover', 'status', 'published', 'featured')}),
        ('English / primary content', {'fields': ('name', 'short_description', 'description')}),
        ('Persian translation (optional)', {'fields': ('name_fa', 'short_description_fa', 'description_fa'), 'classes': ('collapse',)}),
    )
    inlines = (FeatureInline, SpecificationInline, SectionInline, FAQInline, MediaInline)

@admin.register(ProductCategory)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
