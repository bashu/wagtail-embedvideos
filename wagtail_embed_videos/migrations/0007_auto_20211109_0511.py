# Generated by Django 3.1.13 on 2021-11-09 05:11

from django.db import migrations


def add_choose_permission_to_admin_groups(apps, _schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    Permission = apps.get_model("auth.Permission")
    Group = apps.get_model("auth.Group")

    # Get embed video content type
    embedvideo_content_type, _created = ContentType.objects.get_or_create(
        model="embedvideo", app_label="wagtail_embed_videos"
    )

    # Create the Choose permission (if it doesn't already exist)
    choose_embedvideo_permission, _created = Permission.objects.get_or_create(
        content_type=embedvideo_content_type, codename="choose_embedvideo", defaults={"name": "Can choose embed video"}
    )

    # Assign it to all groups which have "Access the Wagtail admin" permission.
    # This emulates the previous behavior, where everyone could choose any embed video in any Collection
    # because choosing wasn't permissioned.
    for group in Group.objects.filter(permissions__codename="access_admin"):
        group.permissions.add(choose_embedvideo_permission)


def remove_choose_permission(apps, _schema_editor):
    """Reverse the above additions of permissions."""
    ContentType = apps.get_model("contenttypes.ContentType")
    Permission = apps.get_model("auth.Permission")
    embedvideo_content_type = ContentType.objects.get(
        model="embedvideo",
        app_label="wagtail_embed_videos",
    )
    # This cascades to Group
    Permission.objects.filter(content_type=embedvideo_content_type, codename="choose_embedvideo").delete()


def get_choose_permission(apps):
    Permission = apps.get_model("auth.Permission")
    ContentType = apps.get_model("contenttypes.ContentType")

    embedvideo_content_type, _created = ContentType.objects.get_or_create(
        model="embedvideo",
        app_label="wagtail_embed_videos",
    )
    return Permission.objects.filter(content_type=embedvideo_content_type, codename__in=["choose_embedvideo"]).first()


def copy_choose_permission_to_collections(apps, _schema_editor):
    Collection = apps.get_model("wagtailcore.Collection")
    Group = apps.get_model("auth.Group")
    GroupCollectionPermission = apps.get_model("wagtailcore.GroupCollectionPermission")

    root_collection = Collection.objects.get(depth=1)

    permission = get_choose_permission(apps)
    if permission:
        for group in Group.objects.filter(permissions=permission):
            GroupCollectionPermission.objects.create(group=group, collection=root_collection, permission=permission)


def remove_choose_permission_from_collections(apps, _schema_editor):
    GroupCollectionPermission = apps.get_model("wagtailcore.GroupCollectionPermission")
    choose_permission = get_choose_permission(apps)
    if choose_permission:
        GroupCollectionPermission.objects.filter(permission=choose_permission).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("wagtail_embed_videos", "0006_auto_20211104_0557"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="embedvideo",
            options={
                "permissions": [("choose_embedvideo", "Can choose embed video")],
                "verbose_name": "embed video",
                "verbose_name_plural": "embed videos",
            },
        ),
        migrations.RunPython(add_choose_permission_to_admin_groups, remove_choose_permission),
        migrations.RunPython(copy_choose_permission_to_collections, remove_choose_permission_from_collections),
    ]
