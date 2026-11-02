from django.db import migrations


def update_contact(apps, schema_editor):
    CompanyProfile = apps.get_model('company', 'CompanyProfile')
    CompanyProfile.objects.using(schema_editor.connection.alias).filter(pk=1).update(
        phone='+98 917 846 2012')


class Migration(migrations.Migration):
    dependencies = [('company', '0005_companyprofile_ceo_name_companyprofile_ceo_name_fa')]
    operations = [migrations.RunPython(update_contact, migrations.RunPython.noop)]
