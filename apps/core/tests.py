from io import BytesIO
from tempfile import TemporaryDirectory
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, Client, override_settings
from apps.customers.models import CustomerOrganization
from apps.products.models import Product, ProductCategory, ProductFeature
from apps.projects.models import Project, ProjectProduct, Industry
from apps.contact.models import Inquiry
from apps.media_library.models import MediaAsset


class WebsiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = CustomerOrganization.objects.create(name='INTERNAL LEGAL NAME', contact_email='private@example.com')
        cls.category = ProductCategory.objects.create(name='Industrial', slug='industrial')
        cls.product = Product.objects.create(name='Published product', slug='published', short_description='Summary', description='Description', published=True, featured=True, category=cls.category)
        cls.draft = Product.objects.create(name='DRAFT SECRET', slug='draft', short_description='Hidden', description='Hidden')
        cls.industry = Industry.objects.create(name='Water', slug='water')
        cls.project = Project.objects.create(title='Public project', slug='public-project', customer=cls.customer, public_customer_name='Approved customer', summary='Summary', description='Description', published=True, publication_authorized=True, featured=True, industry=cls.industry)
        ProjectProduct.objects.create(project=cls.project, product=cls.product)
        ProjectProduct.objects.create(project=cls.project, product=cls.draft)
        cls.private_project = Project.objects.create(title='PRIVATE PROJECT', slug='private-project', customer=cls.customer, summary='Secret', description='Secret')
        ProductFeature.objects.create(product=cls.product, title='HIDDEN FEATURE', published=False)

    def test_pages_and_publication(self):
        for url in ['/', '/products/', '/products/published/', '/projects/', '/projects/public-project/', '/company/', '/engineering/', '/contact/']:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, '<html lang="en" dir="ltr">')
                for secret in ['DRAFT SECRET', 'PRIVATE PROJECT', 'HIDDEN FEATURE', 'INTERNAL LEGAL NAME', 'private@example.com']:
                    self.assertNotContains(response, secret)
        self.assertEqual(self.client.get('/products/draft/').status_code, 404)
        self.assertEqual(self.client.get('/projects/private-project/').status_code, 404)

    def test_project_requires_authorization(self):
        self.private_project.published = True
        with self.assertRaises(ValidationError):
            self.private_project.full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.private_project.save()

    def test_filters(self):
        self.assertContains(self.client.get('/products/?category=industrial'), self.product.name)
        self.assertNotContains(self.client.get('/products/?category=unknown'), self.product.name)
        self.assertContains(self.client.get('/projects/?product=published&industry=water'), self.project.title)
        self.assertNotContains(self.client.get('/projects/?product=draft'), self.project.title)

    def test_contact_workflow_and_throttle(self):
        cache.clear()
        data = {'name':'Customer', 'email':'customer@example.com', 'message':'Please contact us', 'kind':'demo', 'product':self.product.pk}
        self.assertEqual(self.client.post('/contact/', data).status_code, 302)
        self.assertEqual(Inquiry.objects.count(), 1)
        self.assertContains(self.client.post('/contact/', data), 'errorlist')
        self.assertEqual(Inquiry.objects.count(), 1)
        data['product'] = self.draft.pk
        self.client.post('/contact/', data)
        self.assertEqual(Inquiry.objects.count(), 1)

    def test_contact_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/contact/', {'name':'Test'}).status_code, 403)

    def test_admin_pages(self):
        self.assertEqual(self.client.get('/admin/').status_code, 302)
        user = get_user_model().objects.create_superuser(username='admin', email='a@example.com', password='test-password')
        self.client.force_login(user)
        for url in ['/admin/', '/admin/products/product/add/', f'/admin/products/product/{self.product.pk}/change/', f'/admin/projects/project/{self.project.pk}/change/', '/admin/media_library/mediaasset/add/', '/admin/contact/inquiry/']:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_upload_validation(self):
        asset = MediaAsset(title='Invalid', alt_text='Invalid', file=SimpleUploadedFile('evil.svg', b'<svg/>', content_type='image/svg+xml'))
        with self.assertRaises(ValidationError):
            asset.full_clean()
        asset.file = SimpleUploadedFile('fake.png', b'not an image', content_type='image/png')
        with self.assertRaises(ValidationError):
            asset.full_clean()
        stream = BytesIO()
        Image.new('RGB', (10,10)).save(stream, format='PNG')
        asset.file = SimpleUploadedFile('valid.png', stream.getvalue(), content_type='image/png')
        asset.full_clean()

    def test_pagination_preserves_filters(self):
        for i in range(13):
            Product.objects.create(name=f'Product {i}', slug=f'p-{i}', short_description='Text', description='Text', published=True, category=self.category)
        response = self.client.get('/products/?category=industrial')
        self.assertContains(response, 'category=industrial&amp;page=2')

    def test_image_processing_and_gallery(self):
        from apps.products.models import ProductMedia
        stream = BytesIO()
        Image.new('RGB', (2600, 100)).save(stream, format='PNG')
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            asset = MediaAsset.objects.create(title='Screenshot', alt_text='Public screenshot', file=SimpleUploadedFile('screen.png', stream.getvalue(), content_type='image/png'))
            with Image.open(asset.file.path) as image:
                self.assertEqual(image.format, 'WEBP')
                self.assertEqual(image.width, 2400)
            ProductMedia.objects.create(product=self.product, asset=asset, caption='Approved caption')
            response = self.client.get(self.product.get_absolute_url())
            self.assertContains(response, 'Public screenshot')
            self.assertContains(response, 'Approved caption')

    def test_language_switch_persists_and_preserves_page(self):
        response = self.client.post('/i18n/setlang/', {'language': 'fa', 'next': '/products/?category=industrial'})
        self.assertRedirects(response, '/products/?category=industrial')
        self.assertEqual(response.cookies['django_language'].value, 'fa')
        response = self.client.get('/contact/')
        self.assertContains(response, '<html lang="fa" dir="rtl">')
        self.assertContains(response, 'نام و نام خانوادگی')
        self.assertContains(response, 'درخواست دمو')
        self.client.post('/i18n/setlang/', {'language': 'en', 'next': '/contact/'})
        response = self.client.get('/contact/')
        self.assertContains(response, '<html lang="en" dir="ltr">')
        self.assertContains(response, 'Full name')
        self.assertContains(response, 'Demo request')

    def test_editorial_translation_and_fallback(self):
        self.product.name_fa = 'محصول فارسی'
        self.product.description_fa = 'توضیحات فارسی محصول'
        self.product.save()
        self.client.cookies['django_language'] = 'fa'
        response = self.client.get(self.product.get_absolute_url())
        self.assertContains(response, 'محصول فارسی')
        self.assertContains(response, 'توضیحات فارسی محصول')
        self.assertContains(response, self.product.short_description)
        self.client.cookies['django_language'] = 'en'
        response = self.client.get(self.product.get_absolute_url())
        self.assertContains(response, self.product.name)
        self.assertNotContains(response, 'توضیحات فارسی محصول')

    def test_language_redirect_cannot_leave_site(self):
        response = self.client.post('/i18n/setlang/', {'language': 'fa', 'next': 'https://external.example/'})
        self.assertEqual(response.url, '/')

    def test_persian_pages_render_and_hide_private_content(self):
        self.client.cookies['django_language'] = 'fa'
        for url in ['/', '/products/', self.product.get_absolute_url(), '/projects/', self.project.get_absolute_url(), '/company/', '/engineering/', '/contact/']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<html lang="fa" dir="rtl">')
            self.assertNotContains(response, 'INTERNAL LEGAL NAME')


class InteractionPageTests(TestCase):
    def test_home_has_accessible_bilingual_interactions(self):
        for language in ['en', 'fa']:
            self.client.cookies['django_language'] = language
            response = self.client.get('/')
            self.assertContains(response, 'id="ambient-canvas"')
            self.assertContains(response, 'js/ambient.js')
            self.assertNotContains(response, 'class="motion-toggle"')
            self.assertNotContains(response, 'data-studio')
            self.assertContains(response, 'class="icon-moon"')
            self.assertContains(response, 'class="mobile-menu-drawer"')
            self.assertContains(response, 'data-menu-close')
            self.assertContains(response, 'class="image-viewer"')
            self.assertContains(response, 'css/interactions.css')
            self.assertContains(response, 'js/interactions.js')

    def test_leadership_removed_and_import_does_not_restore_it(self):
        from apps.company.models import CompanyProfile
        from django.core.management import call_command
        from io import StringIO
        call_command('import_company_profile', stdout=StringIO())
        call_command('import_company_profile', stdout=StringIO())
        self.assertNotIn('ceo_name', {field.name for field in CompanyProfile._meta.fields})
        for language in ['en', 'fa']:
            self.client.cookies['django_language'] = language
            for url in ['/', '/company/', '/contact/', '/projects/', '/products/']:
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, 'class="leadership"')
                self.assertNotContains(response, 'Chief Executive Officer')
                self.assertNotContains(response, 'CEO:')
