from django import template
from django.utils.translation import get_language
from apps.core.copy import ENGLISH

register = template.Library()

@register.filter(name='ui')
def ui(value):
    return value if (get_language() or 'en').startswith('fa') else ENGLISH.get(str(value), value)

@register.simple_tag(name='ui')
def ui_tag(value):
    return ui(value)

@register.filter
def localized(obj, field):
    if obj is None:
        return ''
    if (get_language() or 'en').startswith('fa'):
        return getattr(obj, field + '_fa', '') or getattr(obj, field, '')
    return getattr(obj, field, '')


@register.simple_tag
def phrase(english, persian):
    """Explicit bilingual copy for presentational content."""
    return persian if (get_language() or 'en').startswith('fa') else english
