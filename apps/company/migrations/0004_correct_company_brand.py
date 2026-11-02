from django.db import migrations


def correct_brand(apps, schema_editor):
    CompanyProfile = apps.get_model('company', 'CompanyProfile')
    for profile in CompanyProfile.objects.using(schema_editor.connection.alias).all():
        updates = {}
        if profile.name in {'Tech Experts', 'استادان فناوری پویا'}:
            updates['name'] = 'Dynamic Tech Experts'
        if profile.introduction.startswith('Tech Experts ('):
            updates['introduction'] = profile.introduction.replace('Tech Experts (', 'Dynamic Tech Experts (', 1)
        if updates:
            CompanyProfile.objects.using(schema_editor.connection.alias).filter(pk=profile.pk).update(**updates)


class Migration(migrations.Migration):
    dependencies = [('company', '0003_alter_companyprofile_name')]
    operations = [migrations.RunPython(correct_brand, migrations.RunPython.noop)]
