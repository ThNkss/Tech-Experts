import uuid
from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError
from django.core.files.base import ContentFile
from pathlib import Path
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from apps.core.models import TimestampedModel


def image_path(instance, filename):
    return f"images/{uuid.uuid4().hex}{Path(filename).suffix.lower()}"


def validate_image_size(value):
    if value.size > 10 * 1024 * 1024:
        raise ValidationError("حداکثر حجم تصویر ۱۰ مگابایت است.")


def validate_raster_image(value):
    try:
        value.seek(0)
        with Image.open(value) as image:
            if image.format not in {'JPEG', 'PNG', 'WEBP'}:
                raise ValidationError('فقط تصاویر JPEG، PNG و WebP پذیرفته می‌شوند.')
            if image.width * image.height > 25_000_000:
                raise ValidationError('ابعاد تصویر بیش از حد بزرگ است.')
            image.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValidationError('فایل تصویر معتبر نیست.') from exc
    finally:
        value.seek(0)


class MediaAsset(TimestampedModel):
    alt_text_fa = models.TextField(blank=True, verbose_name="alt text (Persian)")
    # MVP library intentionally accepts public raster images only.
    file = models.ImageField(upload_to=image_path, validators=[
        FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']), validate_image_size, validate_raster_image])
    title = models.CharField(max_length=200)
    alt_text = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if self.file and not self.file._committed:
            validate_image_size(self.file)
            validate_raster_image(self.file)
            with Image.open(self.file) as source:
                image = ImageOps.exif_transpose(source)
                image.thumbnail((2400, 2400))
                image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
                output = BytesIO()
                image.save(output, format='WEBP', quality=85, exif=b'')
            self.file.save(f'{uuid.uuid4().hex}.webp', ContentFile(output.getvalue()), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
