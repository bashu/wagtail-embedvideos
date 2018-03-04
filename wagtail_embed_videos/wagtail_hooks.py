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
from wagtail_embed_videos.forms import GroupEmbedVideoPermissionFormSet
from wagtail_embed_videos.permissions import permission_policy


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
        return permission_policy.user_has_any_permission(
            request.user, ['add', 'change', 'delete']
        )


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


@hooks.register('register_group_permission_panel')
def register_embed_videos_permissions_panel():
    return GroupEmbedVideoPermissionFormSet
