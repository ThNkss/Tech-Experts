from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from .models import Project, ProjectParty
from django.core.exceptions import ValidationError
from decimal import Decimal


class AbadehProjectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('import_abadeh_project', stdout=StringIO())
        cls.project = Project.objects.get(slug='abadeh-wastewater-treatment-plant')

    def test_import_is_repeatable_and_uses_confirmed_data(self):
        call_command('import_abadeh_project', stdout=StringIO())
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.project.full_clean()
        self.assertIsNone(self.project.customer)
        self.assertIsNone(self.project.completion_date)
        self.assertTrue(self.project.published)
        self.assertTrue(self.project.publication_authorized)
        self.assertEqual(self.project.products.count(), 1)
        self.assertEqual(self.project.products.get().slug, 'horizon-scada')

    def test_project_appears_in_bilingual_portfolio_and_product(self):
        for language, title in [('en', 'Abadeh Wastewater Treatment Plant'), ('fa', 'تصفیه‌خانه فاضلاب آباده')]:
            self.client.cookies['django_language'] = language
            self.assertContains(self.client.get('/projects/?product=horizon-scada&industry=water-and-wastewater'), title)
            self.assertContains(self.client.get(self.project.get_absolute_url()), title)
            self.assertContains(self.client.get('/products/horizon-scada/'), title)

    def test_optional_parties_and_value_are_only_public_when_enabled(self):
        ProjectParty.objects.create(project=self.project, role='client', public_name='PRIVATE CLIENT')
        for order, role in enumerate(ProjectParty.Role.values):
            ProjectParty.objects.create(project=self.project, role=role, public_name=f'Approved {role}',
                public_name_fa=f'FA {role}', published=True, display_order=order)
        self.project.contract_value = Decimal('987654321.25')
        self.project.progress_percent = 0
        self.project.save()
        response = self.client.get(self.project.get_absolute_url())
        self.assertNotContains(response, 'PRIVATE CLIENT')
        self.assertNotContains(response, 'Project value')
        self.assertContains(response, 'value="0"')
        for role in ProjectParty.Role.values:
            self.assertContains(response, f'Approved {role}')
        self.project.show_contract_value = True
        self.project.currency = 'USD'
        self.project.save()
        self.assertContains(self.client.get(self.project.get_absolute_url()), 'USD')
        self.client.cookies['django_language'] = 'fa'
        response = self.client.get(self.project.get_absolute_url())
        for title in ['کارفرما', 'پیمانکار', 'مشاور', 'کارفرمای اصلی', 'مبلغ پروژه']:
            self.assertContains(response, title)
        self.assertContains(response, 'FA consultant')
        self.assertNotContains(response, 'PRIVATE CLIENT')

    def test_progress_and_price_validation(self):
        for invalid in [-1, 101]:
            self.project.progress_percent = invalid
            with self.assertRaises(ValidationError):
                self.project.full_clean()
        self.project.progress_percent = 45
        self.project.status = 'completed'
        with self.assertRaises(ValidationError):
            self.project.full_clean()
        self.project.progress_percent = None
        self.project.full_clean()
        self.assertEqual(self.project.public_progress, 100)
        self.project.show_contract_value = True
        with self.assertRaises(ValidationError):
            self.project.full_clean()
        self.project.contract_value = Decimal('-1')
        with self.assertRaises(ValidationError):
            self.project.full_clean()
        self.project.contract_value = Decimal('0')
        self.project.full_clean()

    def test_completed_project_displays_full_progress(self):
        self.project.status = 'completed'
        self.project.save()
        response = self.client.get(self.project.get_absolute_url())
        self.assertContains(response, 'value="100"')
        self.assertContains(response, '100%')

    def test_board_parties_and_scada_scope_are_published_in_both_languages(self):
        call_command('import_abadeh_project', stdout=StringIO())
        self.assertEqual(self.project.parties.filter(published=True).count(), 6)
        self.assertEqual(self.project.parties.get(role='end_client', published=True).public_name, 'Fars Water and Wastewater Co.')
        self.assertEqual(self.project.parties.get(role='client', published=True).public_name, 'Saabniroo')
        self.assertEqual(self.project.parties.get(role='contractor', published=True).public_name, 'Dynamic Tech Experts')
        for language, expected in [
            ('en', ['Fars Water and Wastewater Co.', 'Tehran Sahab Consulting Engineers',
                'Saabniroo', 'Islamic Development Bank',
                'Software / SCADA developer', 'Dynamic Tech Experts', 'Principal client', 'Contractor']),
            ('fa', ['شرکت آب و فاضلاب استان فارس', 'شرکت مهندسین مشاور تهران سحاب',
                'شرکت ساب نیرو', 'بانک توسعه اسلامی', 'توسعه‌دهنده نرم‌افزار و اسکادا',
                'استادان فناوری پویا', 'کارفرمای اصلی', 'پیمانکار'])]:
            self.client.cookies['django_language'] = language
            response = self.client.get(self.project.get_absolute_url())
            for text in expected:
                self.assertContains(response, text)
        developer = self.project.parties.get(role='software_developer')
        self.assertEqual(developer.public_name, 'Dynamic Tech Experts')
        self.assertTrue(developer.published)

    def test_corrected_roles_retire_the_previous_interpretation(self):
        old_client = ProjectParty.objects.create(project=self.project, role='client',
            public_name='Fars Water and Wastewater Co.', published=True)
        old_contractor = ProjectParty.objects.create(project=self.project, role='contractor',
            public_name='Mahab Ghods–Sabniroo Joint Venture', published=True)
        call_command('import_abadeh_project', stdout=StringIO())
        call_command('import_abadeh_project', stdout=StringIO())
        old_client.refresh_from_db()
        old_contractor.refresh_from_db()
        self.assertFalse(old_client.published)
        self.assertFalse(old_contractor.published)
        self.assertEqual(self.project.parties.filter(published=True).count(), 6)
        for language in ['en', 'fa']:
            self.client.cookies['django_language'] = language
            response = self.client.get(self.project.get_absolute_url())
            self.assertNotContains(response, 'Mahab Ghods')
            self.assertNotContains(response, 'مشارکت مهاب')
            self.assertNotContains(response, 'پیمانکار کل پروژه')
