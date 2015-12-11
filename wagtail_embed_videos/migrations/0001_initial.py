# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import embed_video.fields
import wagtail.wagtailadmin.taggable
import django.db.models.deletion
from django.conf import settings
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('wagtailimages', '0006_add_verbose_names'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmbedVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('url', embed_video.fields.EmbedVideoField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text=None, verbose_name='Tags')),
                ('thumbnail', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Thumbnail', blank=True, to='wagtailimages.Image', null=True)),
                ('uploaded_by_user', models.ForeignKey(blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, wagtail.wagtailadmin.taggable.TagSearchable),
        ),
    ]
