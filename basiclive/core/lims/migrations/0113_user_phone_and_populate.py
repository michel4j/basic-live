# Generated migration to add phone field to User and populate from Project contact_phone

from django.db import migrations, models


def populate_user_phone_from_projects(apps, schema_editor):
    User = apps.get_model('lims', 'User')
    Project = apps.get_model('lims', 'Project')

    for user in User.objects.all():
        # Check project where user is PI
        project = (
            Project.objects.filter(pi_id=user.pk)
            .exclude(contact_phone__isnull=True)
            .exclude(contact_phone='')
            .order_by('-modified')
            .first()
        )
        if not project:
            # Check project where user is a member
            project = (
                Project.objects.filter(memberships__user_id=user.pk)
                .exclude(contact_phone__isnull=True)
                .exclude(contact_phone='')
                .order_by('-modified')
                .first()
            )
        if not project:
            # Check project matching username
            project = (
                Project.objects.filter(name=user.username)
                .exclude(contact_phone__isnull=True)
                .exclude(contact_phone='')
                .first()
            )
        if project and getattr(project, 'contact_phone', None):
            user.phone = project.contact_phone
            user.save(update_fields=['phone'])


def reverse_populate_user_phone(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0112_alter_data_session'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=60, verbose_name='Phone'),
        ),
        migrations.RunPython(
            populate_user_phone_from_projects,
            reverse_code=reverse_populate_user_phone,
        ),
    ]
