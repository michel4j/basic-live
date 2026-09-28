# Generated schema migration to remove auth fields from Project after data migration

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0104_migrate_project_users_data'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='project',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='project',
            name='date_joined',
        ),
        migrations.RemoveField(
            model_name='project',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='project',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='project',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='project',
            name='is_superuser',
        ),
        migrations.RemoveField(
            model_name='project',
            name='last_login',
        ),
        migrations.RemoveField(
            model_name='project',
            name='password',
        ),
        migrations.RemoveField(
            model_name='project',
            name='user_permissions',
        ),
    ]
