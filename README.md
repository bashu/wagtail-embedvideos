WAGTAIL EMBED VIDEOS
====================

Simple app that works similar to wagtailimages, but for embedding YouTube and Vimeo videos and music from SoundCloud. It's an integration of [django-embed-video](https://github.com/yetty/django-embed-video).

WARNING
-------

With recent changes to keep up with Wagtail current versions, we do **not** support versions <= 1.6!

If you use previous versions of Wagtail (<=1.6), please consider using v0.2.5 of `wagtail_embed_videos`.

REQUIREMENTS
------------

You have install `wagtail-embedvideos` package, use the common command:

```
    pip install wagtail-embed-videos
```

You need add `wagtailimages` to the current settings, is by default in any `wagtail` project.

Quick start
-----------

1.	Add "embed_video" and "wagtail_embed_videos" to your INSTALLED_APPS setting like this:

	```python
	INSTALLED_APPS = [
	    ...
	    'embed_video',
	    'wagtail_embed_videos',
	    ...
	]
	```

2.	Run `python manage.py makemigrations` to create the migration for `wagtail_embed_videos` models.

3.	Run `python manage.py migrate` to create the models of `wagtail_embed_videos` app.

4.	Using `wagtail_embed_videos`:

	```python
	    from wagtail_embed_videos.edit_handlers import EmbedVideoChooserPanel


	    class VideoBasedModel(models.Model):
	        video = models.ForeignKey(
	            'wagtail_embed_videos.EmbedVideo',
	            verbose_name="Video",
	            null=True,
	            blank=True,
	            on_delete=models.SET_NULL,
	            related_name='+'
	        )
	        ...
	        panels = [EmbedVideoChooserPanel('video')]
	```

5.	For render your video in a template put `{% load embed_video_tags%}` for load template tags and put this code where you want render your video:

	\`\``html {% video VideoBasedModel.video.url as video %} {% video video 'small' %} {% endvideo %}

```

6. Check [django-embed-video](https://github.com/yetty/django-embed-video) for more documentation.


Use `EmbedVideo` API:
--------------------
You can get access to the model in python with the next instructions:

```python
        # Accessing the EmbedVideoField() in the model 'wagtail_embed_videos.EmbedVideo'
        # this is the field used for storing the url of the embed video
        video_based_model_instanse.video.url

        # Accessing the thumbnail image in the model 'wagtailimages'
        # this is a foreign key to model Image
        video_based_model_instanse.video.thumbnail
```

EmbedVideo Block
----------------

You can use `EmbedVideo` in `StreamFields` too, an example:

```python
    from wagtail_embed_videos.blocks import EmbedVideoChooserBlock

       ...

       class EmbedVideoFormatChoiceBlock(FieldBlock):
            field = forms.ChoiceField(
                choices=(
                    ('left', 'Wrap left'),
                    ('right', 'Wrap right'),
                    ('half', 'Half width'),
                    ('full', 'Full width'),
                )
            )


        class EmbedVideoBlock(StructBlock):
            video = EmbedVideoChooserBlock()
            alignment = ImageFormatChoiceBlock()
            caption = CharBlock()
            attribution = CharBlock(required=False)

            class Meta:
                icon = 'media'


        class StoryBlock(StreamBlock):
            ...
            aligned_video = EmbedVideoBlock(label=_('Aligned video'))
            ...
```

Extend EmbedVideo model
-----------------------

You can extend the `EmbedVideo` model in the same way that `wagtail` image models. Use this setting:`WAGTAILEMBEDVIDEO_VIDEO_MODEL`.

Release Notes
-------------

**v0.3.0**

-	Changed the structure of "AbstractEmbedVideo", because "TagSearchable" is not used anymore;

**v0.2.5**

-	This is the last version compatible with Wagtail <= 1.6, because TagSearchable was deprecated and then removed.

**v0.0.6**

-	Now is possible create video collections.
-	Documentation about extend the embed video model.
-	Documentation about embed video blocks for stream field.

**v0.0.5**

-	Now it shows the video when editing

**v0.0.4**

-	Auto-create thumbnail images in wagtailimages app with tag 'video-thumbnail'
-	EmbedVideoChooserPanel now has a link to create a new embed video instance instead of the form (this is a fix to the problem having nested modals of wagtail)

**v0.0.3**

-	Fixed injection of js file for embed video chooser
-	Removed more unnecessary files
