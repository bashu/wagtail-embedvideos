from django.conf import settings
from django.conf.urls import include, url
from django.core import urlresolvers
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem

from wagtail_embed_videos import admin_urls


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^embed_videos/', include(admin_urls)),
    ]


@hooks.register('construct_main_menu')
def construct_main_menu(request, menu_items):
    pass


class EmbedVideosMenuItem(MenuItem):
    def is_shown(self, request):
        return request.user.has_perm('wagtail_embed_videos.add_embedvideo')


@hooks.register('register_admin_menu_item')
def register_embed_videos_menu_item():
    return EmbedVideosMenuItem(
        _('Embed Videos'),
        urlresolvers.reverse('wagtail_embed_videos_index'),
        classnames='icon icon-media', order=301)


@hooks.register('insert_editor_js')
def editor_js():
    js_files = [
        'wagtail_embed_videos/js/embed-video-chooser.js',
    ]
    js_includes = format_html_join('\n', '<script src="{0}{1}"></script>', (
        (settings.STATIC_URL, filename) for filename in js_files)
    )
    return js_includes + format_html(
        """
        <script>
            window.chooserUrls.embedVideoChooser = '{0}';
        </script>
        """,
        urlresolvers.reverse('wagtail_embed_videos_chooser')
    )


@hooks.register('register_permissions')
def register_permissions():
    embed_video_content_type = ContentType.objects.get(
        app_label='wagtail_embed_videos', model='embedvideo')
    embed_video_permissions = Permission.objects.filter(
        content_type=embed_video_content_type)
    return embed_video_permissions
