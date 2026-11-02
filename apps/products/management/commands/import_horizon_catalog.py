import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.products.models import Product, ProductCategory, ProductFeature, ProductSpecification, ProductSection, ProductFAQ


class Command(BaseCommand):
    help = 'Import the reviewed, bilingual Horizon SCADA catalog. Re-running updates the supplied catalog entries.'

    @transaction.atomic
    def handle(self, *args, **options):
        source = Path(__file__).resolve().parents[2] / 'data' / 'horizon_scada.json'
        data = json.loads(source.read_text(encoding='utf-8'))
        category_data = data['category'].copy()
        category, _ = ProductCategory.objects.update_or_create(slug=category_data.pop('slug'), defaults=category_data)
        product_data = data['product'].copy()
        product, _ = Product.objects.update_or_create(slug=product_data.pop('slug'), defaults={**product_data, 'category': category})
        # Retire only the previous bundled edition; keep administrator-authored content.
        legacy_features = ['Process views that follow the plant', 'A defined model for every signal',
            'Commands with an operational record', 'Alarm handling beyond an active list',
            'History with a configurable archive policy', 'Reports for investigation and handover',
            'Equipment records alongside process data', 'Access tied to role and operating scope',
            'Traceable user and system activity', 'OPC UA acquisition with local buffering']
        product.features.filter(title__in=legacy_features).update(published=False)
        product.sections.filter(key__in=['applications', 'delivery', 'scope']).update(published=False)
        product.faqs.filter(question__in=[
            'Can Horizon connect directly to every PLC?', 'Can operators review historical values and alarm response?',
            'How is access separated between teams or sites?', 'What happens if the agent cannot transfer measurements?',
            'What information is needed for a technical proposal?']).update(published=False)
        product.specifications.filter(name__in=['User environment', 'Field-data interface', 'Operator interface',
            'Operational model', 'Signal definitions', 'Archive policy', 'Historical exports', 'Alarm analysis',
            'Equipment records', 'Access model', 'System sizing']).delete()
        for order, feature in enumerate(data['features'], start=1):
            feature = feature.copy()
            ProductFeature.objects.update_or_create(product=product, title=feature.pop('title'), defaults={**feature, 'display_order': order, 'published': True})
        for order, (name, value, name_fa, value_fa) in enumerate(data['specifications'], start=1):
            ProductSpecification.objects.update_or_create(product=product, name=name, defaults={'value': value, 'name_fa': name_fa, 'value_fa': value_fa, 'display_order': order})
        for order, section in enumerate(data['sections'], start=1):
            section = section.copy()
            ProductSection.objects.update_or_create(product=product, key=section.pop('key'), defaults={**section, 'display_order': order, 'published': True})
        for order, faq in enumerate(data['faqs'], start=1):
            faq = faq.copy()
            ProductFAQ.objects.update_or_create(product=product, question=faq.pop('question'), defaults={**faq, 'display_order': order, 'published': True})
        self.stdout.write(self.style.SUCCESS(f"Horizon SCADA catalog imported: {len(data['features'])} capabilities, {len(data['specifications'])} specifications, {len(data['sections'])} chapters, {len(data['faqs'])} FAQs."))
