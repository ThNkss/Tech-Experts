from django.db import models
from apps.core.models import TimestampedModel


class CustomerOrganization(TimestampedModel):
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=50, blank=True)
    national_id = models.CharField(max_length=30, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.name
