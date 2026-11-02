from django.core.management.base import BaseCommand
from apps.company.models import CompanyProfile


class Command(BaseCommand):
    help = "Import reviewed company copy and business contact details; preserve existing editor content."

    def handle(self, *args, **options):
        profile, created = CompanyProfile.objects.get_or_create(pk=1)
        content = {
            'name': 'Dynamic Tech Experts',
            'name_fa': 'استادان فناوری پویا',
            'introduction': 'Dynamic Tech Experts is a software company based in Shiraz, Iran. We develop and support software products and customer-specific applications, including industrial monitoring and SCADA solutions.',
            'introduction_fa': 'استادان فناوری پویا یک شرکت نرم‌افزاری مستقر در شیراز است. ما در زمینه توسعه و پشتیبانی محصولات نرم‌افزاری و برنامه‌های اختصاصی مشتریان، از جمله راهکارهای پایش صنعتی و اسکادا فعالیت می‌کنیم.',
            'capabilities': 'Custom software development\nSoftware products and technical support\nIndustrial monitoring and SCADA applications',
            'capabilities_fa': 'توسعه نرم‌افزار اختصاصی\nمحصولات نرم‌افزاری و پشتیبانی فنی\nراهکارهای پایش صنعتی و اسکادا',
            'phone': '+98 917 846 2012',
            'address': 'Kouy-e Daneshgah, Shiraz, Fars, Iran',
            'address_fa': 'ایران، فارس، شیراز',
        }
        for field, value in content.items():
            if not getattr(profile, field) or (field == 'name' and getattr(profile, field) == 'استادان فناوری پویا'):
                setattr(profile, field, value)
        profile.save()
        self.stdout.write(self.style.SUCCESS('Company profile imported; existing editorial content preserved.'))
