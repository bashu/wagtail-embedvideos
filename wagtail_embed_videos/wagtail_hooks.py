from django.conf import settings
from django.conf.urls import include, url
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core import urlresolvers
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext

from wagtail.wagtailadmin.search import SearchArea
from wagtail.wagtailadmin.site_summary import SummaryItem
from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem

from wagtail_embed_videos import admin_urls
from wagtail_embed_videos.api.admin.endpoints import EmbedVideosAdminAPIEndpoint
from wagtail_embed_videos.forms import GroupEmbedVideoPermissionFormSet
from wagtail_embed_videos.models import get_embed_video_model
from wagtail_embed_videos.permissions import permission_policy


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^embed_videos/', include(admin_urls, namespace='wagtail_embed_videos', app_name='wagtail_embed_videos')),
    ]


@hooks.register('construct_main_menu')
def construct_main_menu(router):
    router.register_endpoint('embed_video', EmbedVideosAdminAPIEndpoint)


class EmbedVideosMenuItem(MenuItem):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(
            request.user, ['add', 'change', 'delete']
        )


@hooks.register('register_admin_menu_item')
def register_embed_videos_menu_item():
    return EmbedVideosMenuItem(
        _('Embed Videos'),
        urlresolvers.reverse('wagtail_embed_videos:index'),
        name='embed_videos',
        classnames='icon icon-media',
        order=300
    )


@hooks.register('insert_editor_js')
def editor_js():
    # TODO: Perhaps use a halloplugin for embed videos.
    js_files = [
        static('wagtail_embed_videos/js/embed-video-chooser.js'),
    ]
    js_includes = format_html_join(
        '\n', '<script src="{0}{1}"></script>',
        ((filename) for filename in js_files)
    )
    return js_includes + format_html(
        """
        <script>
            window.chooserUrls.embedVideoChooser = '{0}';
        </script>
        """,
        urlresolvers.reverse('wagtail_embed_videos:chooser')
    )


class EmbedVideosSummaryItem(SummaryItem):
    order = 800
    template = 'wagtail_embed_videos/homepage/site_summary_videos.html'

    def get_context(self):
        return {
            'total_videos': get_embed_video_model().objects.count(),
        }


@hooks.register('construct_homepage_summary_items')
def add_images_summary_item(request, items):
    items.append(EmbedVideosSummaryItem(request))


class EmbedVideosSearchArea(SearchArea):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(
            request.user, ['add', 'change', 'delete']
        )


@hooks.register('register_admin_search_area')
def register_embed_videos_search_area():
    return EmbedVideosSearchArea(
        _('Embed videos'),
        urlresolvers.reverse('wagtail_embed_videos:index'),
        name='embed_videos',
        classnames='icon icon-media',
        order=600
    )


@hooks.register('register_group_permission_panel')
def register_embed_video_permissions_panel():
    return GroupEmbedVideoPermissionFormSet


@hooks.register('describe_collection_contents')
def describe_collection_docs(collection):
    embed_videos_count = get_embed_video_model().objects.filter(collection=collection).count()
    if embed_videos_count:
        url = urlresolvers.reverse('wagtail_embed_videos:index') + ('?collection_id=%d' % collection.id)
        return {
            'count': embed_videos_count,
            'count_text': ungettext(
                "%(count)s video",
                "%(count)s videos",
                embed_videos_count
            ) % {'count': embed_videos_count},
            'url': url,
        }
