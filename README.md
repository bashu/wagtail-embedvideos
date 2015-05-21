# WAGTAIL EMBED VIDEOS

Simple app that works similar to wagtailimages, but for embedding YouTube and Vimeo videos and music from SoundCloud.
It's an integration of [django-embed-video](https://github.com/yetty/django-embed-video)

## REQUIREMENTS

        pip install django-embed-video


## Quick start

1. Add "embed_video" and "wagtail_embed_videos" to your INSTALLED_APPS setting like this:

        INSTALLED_APPS = (
            ...
            'embed_video',
            'wagtail_embed_videos',
            ...
        )

2. Run `python manage.py makemigrations` to create the migration for wagtail_embed_videos models

3. Run `python manage.py migrate` to create the models of wagtail_embed_videos app

3. Using wagtail_embed_videos:

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
            
        # accessing the EmbedVideoField() in the model EmbedVideo
        # this is the field used for storing the url of the embed video
        video_based_model_instanse.video.url
        

4. Check [django-embed-video](https://github.com/yetty/django-embed-video) for more documentation
