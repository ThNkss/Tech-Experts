from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PublishedModel(TimestampedModel):
    published = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    class Meta:
        abstract = True
