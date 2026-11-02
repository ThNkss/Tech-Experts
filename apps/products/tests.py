from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from apps.company.models import CompanyProfile
from .models import Product, ProductFeature, ProductSection, ProductFAQ


class ProductCatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('import_horizon_catalog', stdout=StringIO())
        cls.product = Product.objects.get(slug='horizon-scada')
        CompanyProfile.objects.create(name='Dynamic Tech Experts', phone='+98 917 846 2012')

    def test_import_is_repeatable_and_valid(self):
        call_command('import_horizon_catalog', stdout=StringIO())
        self.assertEqual(Product.objects.filter(slug='horizon-scada').count(), 1)
        self.assertEqual(self.product.features.filter(published=True).count(), 6)
        self.assertEqual(self.product.specifications.count(), 8)
        self.assertEqual(self.product.sections.filter(published=True).count(), 9)
        self.assertEqual(self.product.faqs.filter(published=True).count(), 4)
        for model in (Product, ProductFeature, ProductSection, ProductFAQ):
            for obj in model.objects.all():
                obj.full_clean()

    def test_bilingual_catalog_and_company_identity(self):
        for language, section_text in [('en', 'Several sites, one operational workspace'),
                                           ('fa', 'چند سایت در یک محیط یکپارچه')]:
            self.client.cookies['django_language'] = language
            response = self.client.get(self.product.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, section_text)
            self.assertNotContains(response, 'class="leadership"')
            self.assertContains(response, 'tel:+989178462012')
            self.assertContains(response, 'id="specifications"')
            self.assertContains(response, 'id="questions"')
            self.assertContains(response, 'OPC UA')
            self.assertNotContains(response, '639 8026')
            self.assertNotContains(self.client.get('/company/'), 'class="leadership"')

    def test_unpublished_editorial_content_stays_hidden(self):
        ProductSection.objects.create(product=self.product, key='internal', title='PRIVATE CATALOG SECTION', body='Hidden', published=False)
        ProductFAQ.objects.create(product=self.product, question='PRIVATE CATALOG QUESTION', answer='Hidden', published=False)
        response = self.client.get(self.product.get_absolute_url())
        self.assertNotContains(response, 'PRIVATE CATALOG SECTION')
        self.assertNotContains(response, 'PRIVATE CATALOG QUESTION')

    def test_engineering_explains_process_analysis(self):
        self.client.cookies['django_language'] = 'fa'
        response = self.client.get('/engineering/')
        for term in ['AS-IS', 'TO-BE', 'ERD', 'توسعه افزایشی', 'راستی‌آزمایی و انتشار', 'بهره‌برداری و بهبود', 'معیارهای پذیرش']:
            self.assertContains(response, term)

    def test_catalog_explains_implemented_workflows(self):
        self.client.cookies['django_language'] = 'fa'
        response = self.client.get(self.product.get_absolute_url())
        for anchor in ['hierarchy', 'hmi', 'alarms', 'alarm-reports', 'history', 'commands', 'access', 'integration', 'evolution']:
            self.assertContains(response, f'id="section-{anchor}"')
        for text in ['UserPermissionOverride', 'RolePermission', 'ScopeAssignment', 'ISA‑18.2',
                     'TagHistory', 'Active-Unack', 'میانگین زمانی', 'نمونه آموزشی', 'کیفیت منبع سیگنال']:
            self.assertContains(response, text)
        self.assertContains(response, 'class="hda-table"')
        self.assertNotContains(response, 'سه نوع داده')

    def test_import_retires_bundled_content_and_preserves_custom_content(self):
        legacy = ProductFeature.objects.create(product=self.product, title='A defined model for every signal', published=True)
        custom = ProductFeature.objects.create(product=self.product, title='CUSTOM APPROVED CAPABILITY', published=True)
        call_command('import_horizon_catalog', stdout=StringIO())
        legacy.refresh_from_db()
        custom.refresh_from_db()
        self.assertFalse(legacy.published)
        self.assertTrue(custom.published)
        self.assertNotContains(self.client.get(self.product.get_absolute_url()), legacy.title)
        self.assertContains(self.client.get(self.product.get_absolute_url()), custom.title)
