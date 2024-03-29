# Generated by Django 2.2.24 on 2021-11-03 07:46

from django.db import migrations


def add_embedvideo_permissions_to_admin_groups(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    Permission = apps.get_model("auth.Permission")
    Group = apps.get_model("auth.Group")

    # Get embed video permissions
    embedvideo_content_type, _created = ContentType.objects.get_or_create(
        model="embedvideo", app_label="wagtail_embed_videos"
    )

    add_embedvideo_permission, _created = Permission.objects.get_or_create(
        content_type=embedvideo_content_type, codename="add_embedvideo", defaults={"name": "Can add embed video"}
    )
    change_embedvideo_permission, _created = Permission.objects.get_or_create(
        content_type=embedvideo_content_type, codename="change_embedvideo", defaults={"name": "Can change embed video"}
    )
    delete_embedvideo_permission, _created = Permission.objects.get_or_create(
        content_type=embedvideo_content_type, codename="delete_embedvideo", defaults={"name": "Can delete embed video"}
    )

    # Assign it to Editors and Moderators groups
    for group in Group.objects.filter(name__in=["Editors", "Moderators"]):
        group.permissions.add(add_embedvideo_permission, change_embedvideo_permission, delete_embedvideo_permission)


def remove_embedvideo_permissions(apps, schema_editor):
    """Reverse the above additions of permissions."""
    ContentType = apps.get_model("contenttypes.ContentType")
    Permission = apps.get_model("auth.Permission")
    embedvideo_content_type = ContentType.objects.get(
        model="embedvideo",
        app_label="wagtail_embed_videos",
    )
    # This cascades to Group
    Permission.objects.filter(
        content_type=embedvideo_content_type, codename__in=("add_embedvideo", "change_embedvideo", "delete_embedvideo")
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("wagtail_embed_videos", "0003_embedvideo_collection"),
    ]

    operations = [
        migrations.RunPython(add_embedvideo_permissions_to_admin_groups, remove_embedvideo_permissions),
    ]
