# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
from django.db import migrations


def add_embed_videos_permissions_to_admin_groups(apps, schema_editor):
    ContentType = apps.get_model('contenttypes.ContentType')
    Permission = apps.get_model('auth.Permission')
    Group = apps.get_model('auth.Group')

    # Get embed permissions
    embedvideo_content_type, _created = ContentType.objects.get_or_create(
        model='embedvideo',
        app_label='wagtail_embed_videos',
        defaults={'name': 'embed'} if DJANGO_VERSION < (1, 8) else {}
    )

    add_embed_permission, _created = Permission.objects.get_or_create(
        content_type=embedvideo_content_type,
        codename='add_embed_video',
        defaults={'name': 'Can add embed video'}
    )
    change_embed_permission, _created = Permission.objects.get_or_create(
        content_type=embedvideo_content_type,
        codename='change_embed_video',
        defaults={'name': 'Can change embed video'}
    )
    delete_embed_permission, _created = Permission.objects.get_or_create(
        content_type=embedvideo_content_type,
        codename='delete_embed_video',
        defaults={'name': 'Can delete embed video'}
    )

    # Assign it to Editors and Moderators groups
    for group in Group.objects.filter(name__in=['Editors', 'Moderators']):
        group.permissions.add(add_embed_permission, change_embed_permission, delete_embed_permission)


def remove_embed_videos_permissions(apps, schema_editor):
    """Reverse the above additions of permissions."""
    ContentType = apps.get_model('contenttypes.ContentType')
    Permission = apps.get_model('auth.Permission')
    embed_video_content_type = ContentType.objects.get(
        model='embedvideo',
        app_label='wagtail_embed_videos',
    )
    # This cascades to Group
    Permission.objects.filter(
        content_type=embed_video_content_type,
        codename__in=('add_embed_video', 'change_embed_video', 'delete_embed_video')
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('wagtail_embed_videos', '0001_initial'),

        # Need to run wagtailcores initial data migration to make sure the groups are created
        ('wagtailcore', '0002_initial_data'),
    ]

    operations = [
        migrations.RunPython(add_embed_videos_permissions_to_admin_groups, remove_embed_videos_permissions),
    ]
