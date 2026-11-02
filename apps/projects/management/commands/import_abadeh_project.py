from django.core.management import BaseCommand, call_command
from django.db import transaction
from apps.products.models import Product
from apps.projects.models import Industry, Project, ProjectProduct, ProjectParty


class Command(BaseCommand):
    help = 'Publish the approved bilingual Abadeh wastewater project and link it to Horizon SCADA.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not Product.objects.filter(slug='horizon-scada').exists():
            call_command('import_horizon_catalog', stdout=self.stdout)
        product = Product.objects.get(slug='horizon-scada')
        industry, _ = Industry.objects.update_or_create(slug='water-and-wastewater', defaults={
            'name': 'Water and wastewater', 'name_fa': 'آب و فاضلاب'})
        existing_status = Project.objects.filter(slug='abadeh-wastewater-treatment-plant').values_list('status', flat=True).first()
        project, _ = Project.objects.update_or_create(slug='abadeh-wastewater-treatment-plant', defaults={
            'title': 'Abadeh Wastewater Treatment Plant',
            'title_fa': 'تصفیه‌خانه فاضلاب آباده',
            'summary': 'Development of Horizon SCADA for process supervision, alarm handling, and operational records at Abadeh wastewater treatment plant.',
            'summary_fa': 'توسعه سامانه اسکادا Horizon برای پایش فرایند، رسیدگی به آلارم‌ها و مدیریت سوابق بهره‌برداری تصفیه‌خانه فاضلاب آباده.',
            'description': 'Dynamic Tech Experts is the contractor and developer of the Horizon SCADA software for Abadeh wastewater treatment plant. Saabniroo is the client for this software project, and Fars Water and Wastewater Co. is the principal client. Tehran Sahab Consulting Engineers is the project consultant; Islamic Development Bank is the financier of the wider plant project.\n\nDynamic Tech Experts develops Horizon SCADA for the Abadeh wastewater treatment plant in Fars Province, Iran. The application brings process views, equipment information, tags, alarms, and operational records into a browser-based supervisory environment.\n\nThe software includes process views for screening, grit removal, lagoons, pumping, and chemical systems. Its equipment hierarchy links each measurement and event to the relevant operating unit, providing a route from a process overview to the details of individual assets.',
            'description_fa': 'استادان فناوری پویا پیمانکار و توسعه‌دهنده نرم‌افزار اسکادا Horizon برای تصفیه‌خانه فاضلاب آباده است. کارفرمای این پروژه نرم‌افزاری، شرکت ساب نیرو و کارفرمای اصلی، شرکت آب و فاضلاب استان فارس است. شرکت مهندسین مشاور تهران سحاب، مشاور پروژه و بانک توسعه اسلامی، تأمین‌کننده مالی پروژه تصفیه‌خانه هستند.\n\nاستادان فناوری پویا توسعه نرم‌افزار اسکادا Horizon را برای تصفیه‌خانه فاضلاب آباده در استان فارس انجام می‌دهد. برنامه، نماهای فرایندی، اطلاعات تجهیزات، تگ‌ها، آلارم‌ها و سوابق بهره‌برداری را در یک محیط نظارتی تحت وب کنار هم قرار می‌دهد.\n\nنرم‌افزار شامل نماهای فرایندی آشغال‌گیری، دانه‌گیری، لاگون‌ها، ایستگاه پمپاژ و سامانه‌های شیمیایی است. ساختار تجهیزات، هر اندازه‌گیری و رویداد را به واحد عملیاتی مربوط متصل می‌کند تا پیمایش از نمای کلی فرایند تا جزئیات تجهیز امکان‌پذیر باشد.\n\nبرای روشن‌شدن مدل اطلاعاتی، مسیر زیر را می‌توان به‌صورت نمونه در نظر گرفت: سازمان بهره‌بردار ← سایت تصفیه‌خانه آباده ← ناحیه پمپاژ ← واحد کاری پمپاژ ← واحد گروه پمپ‌ها ← پمپ نمونه ← تگ‌های وضعیت، دبی و فرمان. در این ساختار، تاریخچه و آلارم به تگ مربوط و سابقه سرویس به تجهیز متصل می‌شوند. این مسیر، نمونه آموزشی پیکربندی است و کد واقعی تجهیزات یا تگ‌های سایت را منتشر نمی‌کند.',
            'solution': 'OPC UA provides the implemented field-data interface. Tag definitions connect each measurement, status, and command to its equipment, engineering unit, and permitted range. HMI views use that model to display operating states and values.\n\nThe application supports alarm acknowledgement and history, tag trends and historical reports, equipment run/stop records and service entries. Role permissions and resource scopes define which information and operations are available to each user. The related product catalog describes these software capabilities in detail.',
            'solution_fa': 'رابط میدانی پیاده‌سازی‌شده OPC UA است. هر تگ، اندازه‌گیری، وضعیت یا فرمان را به تجهیز، واحد مهندسی و محدوده مجاز مربوط پیوند می‌دهد. نماهای HMI از همین مدل برای نمایش وضعیت و مقادیر استفاده می‌کنند.\n\nبرنامه، تأیید و تاریخچه آلارم، روند تگ و گزارش تاریخی، سوابق روشن و خاموش تجهیز و ثبت سرویس را پشتیبانی می‌کند. مجوز نقش و دامنه منابع مشخص می‌کنند هر کاربر به چه اطلاعات و عملیاتی دسترسی دارد. شرح این قابلیت‌های نرم‌افزار در کاتالوگ محصول مرتبط آمده است.',
            'location': 'Abadeh, Fars Province, Iran',
            'location_fa': 'ایران، استان فارس، آباده',
            'industry': industry,
            'status': existing_status or 'ongoing',
            'published': True,
            'publication_authorized': True,
            'featured': True,
        })
        # User-confirmed contractual roles for our SCADA project supersede the board interpretation.
        project.parties.filter(role='client', public_name='Fars Water and Wastewater Co.').update(published=False)
        project.parties.filter(role='contractor', public_name='Mahab Ghods–Sabniroo Joint Venture').update(published=False)
        approved_parties = [
            ('end_client', 'Fars Water and Wastewater Co.', 'شرکت آب و فاضلاب استان فارس'),
            ('client', 'Saabniroo', 'شرکت ساب نیرو'),
            ('contractor', 'Dynamic Tech Experts', 'استادان فناوری پویا'),
            ('consultant', 'Tehran Sahab Consulting Engineers', 'شرکت مهندسین مشاور تهران سحاب'),
            ('financier', 'Islamic Development Bank', 'بانک توسعه اسلامی'),
            ('software_developer', 'Dynamic Tech Experts', 'استادان فناوری پویا'),
        ]
        for order, (role, name, name_fa) in enumerate(approved_parties):
            ProjectParty.objects.update_or_create(project=project, role=role, public_name=name,
                defaults={'public_name_fa': name_fa, 'published': True, 'display_order': order})
        ProjectProduct.objects.update_or_create(project=project, product=product, defaults={
            'role': 'SCADA software development for wastewater process supervision'})
        project.full_clean()
        self.stdout.write(self.style.SUCCESS('Abadeh wastewater project published and linked to Horizon SCADA.'))
