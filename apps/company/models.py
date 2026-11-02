from django.db import models
from apps.core.models import TimestampedModel


class CompanyProfile(TimestampedModel):
    name_fa = models.TextField(blank=True, verbose_name="name (Persian)")
    tagline_fa = models.TextField(blank=True, verbose_name="tagline (Persian)")
    introduction_fa = models.TextField(blank=True, verbose_name="introduction (Persian)")
    capabilities_fa = models.TextField(blank=True, verbose_name="capabilities (Persian)")
    address_fa = models.TextField(blank=True, verbose_name="address (Persian)")
    name = models.CharField(max_length=200, default="Dynamic Tech Experts")
    tagline = models.CharField(max_length=250, blank=True)
    introduction = models.TextField(blank=True)
    capabilities = models.TextField(blank=True, help_text="هر توانمندی در یک خط")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
