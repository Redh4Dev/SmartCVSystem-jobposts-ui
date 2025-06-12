# authx/migrations/0002_seed_roles.py
from django.db import migrations

def create_default_roles(apps, schema_editor):
    Role = apps.get_model('authx', 'Role')
    Role.objects.bulk_create([
        Role(role_name='recruiter',  role_description='Can post jobs and manage applicants'),
        Role(role_name='candidate',  role_description='Seeks and applies for posted positions'),
        Role(role_name='company_hr', role_description=' Company HR personnel who review and onboard talent'),
    ], ignore_conflicts=True)  # ignore_conflicts=True so you can re-run safely

def remove_default_roles(apps, schema_editor):
    Role = apps.get_model('authx', 'Role')
    Role.objects.filter(role_name__in=['recruiter','candidate','company_hr']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('authx', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_roles, reverse_code=remove_default_roles),
    ]
