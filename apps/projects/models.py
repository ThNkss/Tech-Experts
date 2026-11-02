from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import get_language
from django.db.models import Q, F
from django.urls import reverse
from apps.core.models import PublishedModel


class Industry(models.Model):
    name_fa = models.TextField(blank=True, verbose_name="name (Persian)")
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return (self.name_fa or self.name) if (get_language() or 'en').startswith('fa') else self.name


class Project(PublishedModel):
    title_fa = models.TextField(blank=True, verbose_name="title (Persian)")
    public_customer_name_fa = models.TextField(blank=True, verbose_name="public customer name (Persian)")
    summary_fa = models.TextField(blank=True, verbose_name="summary (Persian)")
    description_fa = models.TextField(blank=True, verbose_name="description (Persian)")
    challenges_fa = models.TextField(blank=True, verbose_name="challenges (Persian)")
    solution_fa = models.TextField(blank=True, verbose_name="solution (Persian)")
    location_fa = models.TextField(blank=True, verbose_name="location (Persian)")
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, allow_unicode=True)
    customer = models.ForeignKey('customers.CustomerOrganization', null=True, blank=True, on_delete=models.PROTECT, related_name='projects', help_text='Assign the contracting organization only when confirmed.')
    public_customer_name = models.CharField(max_length=200, blank=True, help_text='فقط نامی که اجازه انتشار آن را دارید')
    publication_authorized = models.BooleanField(default=False)
    summary = models.CharField(max_length=350)
    description = models.TextField()
    challenges = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    industry = models.ForeignKey(Industry, null=True, blank=True, on_delete=models.SET_NULL)
    products = models.ManyToManyField('products.Product', through='ProjectProduct', related_name='projects')
    cover = models.ForeignKey('media_library.MediaAsset', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('ongoing', 'در حال اجرا'), ('completed', 'تکمیل‌شده')], default='ongoing')

    progress_percent = models.PositiveSmallIntegerField(null=True, blank=True,
        validators=[MaxValueValidator(100)], help_text='Optional verified progress, 0–100. Completed projects display 100%.')
    contract_value = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)], help_text='Optional project value. Hidden publicly unless publication is enabled below.')
    currency = models.CharField(max_length=3, choices=[('IRR', 'Iranian rial'), ('IRT', 'Toman'), ('USD', 'US dollar'), ('EUR', 'Euro')], default='IRR')
    show_contract_value = models.BooleanField(default=False, help_text='Explicitly permit displaying the project value on the public page.')

    @property
    def public_progress(self):
        return 100 if self.status == 'completed' else self.progress_percent

    def clean(self):
        super().clean()
        if self.status == 'completed' and self.progress_percent not in (None, 100):
            raise ValidationError({'progress_percent': 'Completed projects must have 100% progress or leave the field empty.'})
        if self.show_contract_value and self.contract_value is None:
            raise ValidationError({'contract_value': 'Enter a project value before publishing it.'})

    class Meta:
        ordering = ['-created_at']
        constraints = [models.CheckConstraint(condition=Q(completion_date__isnull=True) | Q(start_date__isnull=True) | Q(completion_date__gte=F('start_date')), name='project_dates_valid'),
                       models.CheckConstraint(condition=Q(published=False) | Q(publication_authorized=True), name='project_publication_authorized'),
                       models.CheckConstraint(condition=Q(progress_percent__isnull=True) | Q(progress_percent__lte=100), name='project_progress_valid'),
                       models.CheckConstraint(condition=~Q(status='completed') | Q(progress_percent__isnull=True) | Q(progress_percent=100), name='completed_project_progress'),
                       models.CheckConstraint(condition=Q(contract_value__isnull=True) | Q(contract_value__gte=0), name='project_value_nonnegative'),
                       models.CheckConstraint(condition=Q(show_contract_value=False) | Q(contract_value__isnull=False), name='public_project_value_present')]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', args=[self.slug])


class ProjectProduct(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    role = models.CharField(max_length=250, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['project', 'product'], name='unique_project_product')]


class ProjectMedia(models.Model):
    caption_fa = models.TextField(blank=True, verbose_name="caption (Persian)")
    project = models.ForeignKey(Project, related_name='gallery', on_delete=models.CASCADE)
    asset = models.ForeignKey('media_library.MediaAsset', on_delete=models.PROTECT)
    caption = models.CharField(max_length=250, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'pk']
        constraints = [models.UniqueConstraint(fields=['project', 'asset'], name='unique_project_asset')]


class ProjectParty(models.Model):
    class Role(models.TextChoices):
        CLIENT = 'client', 'Client / کارفرما'
        CONTRACTOR = 'contractor', 'Contractor / پیمانکار'
        CONSULTANT = 'consultant', 'Consultant / مشاور'
        END_CLIENT = 'end_client', 'Principal client / کارفرمای اصلی'
        FINANCIER = 'financier', 'Financier / تأمین‌کننده مالی'
        SOFTWARE_DEVELOPER = 'software_developer', 'Software / SCADA developer / توسعه‌دهنده نرم‌افزار و اسکادا'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='parties')
    role = models.CharField(max_length=20, choices=Role.choices)
    organization = models.ForeignKey('customers.CustomerOrganization', on_delete=models.PROTECT,
        null=True, blank=True, help_text='Optional internal organization record; never displayed automatically.')
    public_name = models.CharField(max_length=200, help_text='Approved public name of this project party.')
    public_name_fa = models.CharField(max_length=200, blank=True)
    published = models.BooleanField(default=False, help_text='Publish this party’s approved name.')
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'pk']

    def __str__(self):
        return f'{self.get_role_display()}: {self.public_name}'
