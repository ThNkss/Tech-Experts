from django.db import models
from apps.core.models import TimestampedModel

class Inquiry(TimestampedModel):
    name = models.CharField(max_length=150)
    organization = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    product = models.ForeignKey('products.Product', null=True, blank=True, on_delete=models.SET_NULL)
    kind = models.CharField(max_length=20, choices=[('contact', 'تماس'), ('demo', 'درخواست دمو')], default='contact')
    message = models.TextField(max_length=5000)
    handled = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} — {self.get_kind_display()}'
