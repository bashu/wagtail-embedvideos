# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django.db.models.deletion
import embed_video.fields
import taggit.managers
import wagtail.search.index
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("taggit", "0002_auto_20150616_2121"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("wagtailimages", "0018_remove_rendition_filter"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmbedVideo",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Title")),
                ("url", embed_video.fields.EmbedVideoField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True, help_text=None, through="taggit.TaggedItem", to="taggit.Tag", verbose_name="Tags"
                    ),
                ),
                (
                    "thumbnail",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.Image",
                        verbose_name="Thumbnail",
                    ),
                ),
                (
                    "uploaded_by_user",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
    ]
