# Generated data migration to migrate Project auth data to User and ProjectMembership

from django.db import migrations
from django.utils import timezone


def migrate_project_data_to_users(apps, schema_editor):
    Project = apps.get_model('lims', 'Project')
    User = apps.get_model('lims', 'User')
    ProjectMembership = apps.get_model('lims', 'ProjectMembership')
    SSHKey = apps.get_model('lims', 'SSHKey')
    ActivityLog = apps.get_model('lims', 'ActivityLog')
    SupportRecord = apps.get_model('crm', 'SupportRecord')
    BeamlineSupport = apps.get_model('schedule', 'BeamlineSupport')
    Access = apps.get_model('acl', 'Access')
    AccessList = apps.get_model('acl', 'AccessList')

    for project in Project.objects.all():
        username = getattr(project, 'username', None) or getattr(project, 'name', None)
        if not username:
            continue

        # Get or create corresponding User account
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': getattr(project, 'first_name', '') or '',
                'last_name': getattr(project, 'last_name', '') or '',
                'email': getattr(project, 'email', '') or getattr(project, 'contact_email', '') or '',
                'name': getattr(project, 'name', '') or '',
                'password': getattr(project, 'password', '') or '',
                'is_active': getattr(project, 'is_active', True),
                'is_staff': getattr(project, 'is_staff', False),
                'is_superuser': getattr(project, 'is_superuser', False),
                'date_joined': getattr(project, 'date_joined', None) or timezone.now(),
                'last_login': getattr(project, 'last_login', None),
            }
        )

        # Set project PI
        if not project.pi_id:
            project.pi = user
            project.save(update_fields=['pi'])

        # Create PI ProjectMembership
        ProjectMembership.objects.get_or_create(
            user=user,
            project=project,
            defaults={'role': 'PI'}
        )

        # Re-link SSHKeys
        for key in SSHKey.objects.filter(project=project):
            key.user = user
            key.save(update_fields=['user'])

        # Migrate ActivityLog records: re-link entries for this project to the new User
        ActivityLog.objects.filter(project=project).update(user_id=user.pk)
        ActivityLog.objects.filter(user_id=project.pk).update(user_id=user.pk)

        # Migrate SupportRecord staff if pointing to this project
        SupportRecord.objects.filter(staff_id=project.pk).update(staff_id=user.pk)

        # Migrate BeamlineSupport staff
        BeamlineSupport.objects.filter(staff_id=project.pk).update(staff_id=user.pk)

        # Migrate Access user
        Access.objects.filter(user_id=project.pk).update(user_id=user.pk)

        # Migrate AccessList users M2M
        for al in AccessList.objects.filter(users__id=project.pk):
            al.users.add(user)

    # Clean up any dangling IDs before constraints are added
    valid_user_ids = set(User.objects.values_list('pk', flat=True))
    ActivityLog.objects.exclude(user_id__in=valid_user_ids).update(user_id=None)
    SupportRecord.objects.exclude(staff_id__in=valid_user_ids).update(staff_id=None)
    SSHKey.objects.exclude(user_id__in=valid_user_ids).update(user_id=None)
    BeamlineSupport.objects.exclude(staff_id__in=valid_user_ids).update(staff_id=None)
    Access.objects.exclude(user_id__in=valid_user_ids).update(user_id=None)


def reverse_migrate_project_data_to_users(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0103_add_user_and_membership'),
        ('crm', '0081_alter_supportrecord_project'),
        ('schedule', '0006_alter_beamtime_project'),
        ('notebooks', '0003_alter_notebook_project'),
    ]

    operations = [
        migrations.RunPython(
            migrate_project_data_to_users,
            reverse_code=reverse_migrate_project_data_to_users,
        ),
    ]
