from django.db import models
from django.utils.translation import get_language
from django.urls import reverse
from apps.core.models import PublishedModel, TimestampedModel


class ProductCategory(models.Model):
    name_fa = models.TextField(blank=True, verbose_name="name (Persian)")
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return (self.name_fa or self.name) if (get_language() or 'en').startswith('fa') else self.name


class Product(PublishedModel):
    name_fa = models.TextField(blank=True, verbose_name="name (Persian)")
    short_description_fa = models.TextField(blank=True, verbose_name="short description (Persian)")
    description_fa = models.TextField(blank=True, verbose_name="description (Persian)")
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, allow_unicode=True)
    short_description = models.CharField(max_length=350)
    description = models.TextField()
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL)
    cover = models.ForeignKey('media_library.MediaAsset', null=True, blank=True,
                              on_delete=models.SET_NULL, related_name='+')
    status = models.CharField(max_length=20, choices=[('active', 'فعال'), ('coming', 'به‌زودی'), ('retired', 'پایان پشتیبانی')], default='active')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return (self.name_fa or self.name) if (get_language() or 'en').startswith('fa') else self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])


class ProductFeature(models.Model):
    title_fa = models.TextField(blank=True, verbose_name="title (Persian)")
    description_fa = models.TextField(blank=True, verbose_name="description (Persian)")
    product = models.ForeignKey(Product, related_name='features', on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ForeignKey('media_library.MediaAsset', null=True, blank=True, on_delete=models.SET_NULL)
    display_order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'pk']


class ProductSpecification(models.Model):
    name_fa = models.TextField(blank=True, verbose_name="name (Persian)")
    value_fa = models.TextField(blank=True, verbose_name="value (Persian)")
    product = models.ForeignKey(Product, related_name='specifications', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    value = models.CharField(max_length=400)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'pk']


class ProductMedia(models.Model):
    caption_fa = models.TextField(blank=True, verbose_name="caption (Persian)")
    product = models.ForeignKey(Product, related_name='gallery', on_delete=models.CASCADE)
    asset = models.ForeignKey('media_library.MediaAsset', on_delete=models.PROTECT)
    caption = models.CharField(max_length=250, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'pk']
        constraints = [models.UniqueConstraint(fields=['product', 'asset'], name='unique_product_asset')]


class ProductSection(models.Model):
    product = models.ForeignKey(Product, related_name='sections', on_delete=models.CASCADE)
    key = models.SlugField(help_text='Stable catalog anchor, for example integration or delivery.')
    diagram = models.CharField(max_length=20, blank=True, choices=[
        ('hierarchy', 'Equipment hierarchy'), ('alarms', 'Alarm lifecycle'),
        ('access', 'Access decision'), ('integration', 'Multi-site integration'),
        ('history', 'Historical reporting')])
    image = models.ForeignKey('media_library.MediaAsset', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    image_caption = models.CharField(max_length=250, blank=True)
    image_caption_fa = models.CharField(max_length=250, blank=True)
    nav_title = models.CharField(max_length=60, blank=True, help_text='Optional short navigation label.')
    nav_title_fa = models.CharField(max_length=60, blank=True)
    title = models.CharField(max_length=200)
    title_fa = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    body_fa = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'pk']
        constraints = [models.UniqueConstraint(fields=['product', 'key'], name='unique_product_section_key')]

    def __str__(self):
        return self.title


class ProductFAQ(models.Model):
    product = models.ForeignKey(Product, related_name='faqs', on_delete=models.CASCADE)
    question = models.CharField(max_length=250)
    question_fa = models.CharField(max_length=250, blank=True)
    answer = models.TextField()
    answer_fa = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'pk']

    def __str__(self):
        return self.question
