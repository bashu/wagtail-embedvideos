# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtail_embed_videos', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='embedvideo',
            options={'verbose_name': 'V\xeddeo', 'verbose_name_plural': 'V\xeddeos'},
        ),
        migrations.AlterField(
            model_name='embedvideo',
            name='thumbnail',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Miniatura', blank=True, to='wagtailimages.Image', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='embedvideo',
            name='title',
            field=models.CharField(max_length=255, verbose_name='T\xedtulo'),
            preserve_default=True,
        ),
    ]
