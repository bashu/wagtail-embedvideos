from django.urls import include, path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from wagtail.admin.menu import MenuItem
from wagtail.admin.search import SearchArea

# from wagtail.admin.site_summary import SummaryItem
from wagtail.admin.admin_url_finder import ModelAdminURLFinder, register_admin_url_finder
from wagtail.core import hooks

from wagtail_embed_videos import admin_urls, get_embed_video_model
from wagtail_embed_videos.forms import GroupEmbedVideoPermissionFormSet
from wagtail_embed_videos.permissions import permission_policy
from wagtail_embed_videos.views.bulk_actions import (
    AddTagsBulkAction, AddToCollectionBulkAction, DeleteBulkAction)


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        path("embed_videos/", include(admin_urls, namespace="wagtail_embed_videos")),
    ]


@hooks.register("construct_main_menu")
def construct_main_menu(request, menu_items):
    # TODO: register endpoint
    pass


class EmbedVideosMenuItem(MenuItem):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(request.user, ["add", "change", "delete"])


@hooks.register("register_admin_menu_item")
def register_embedvideos_menu_item():
    return EmbedVideosMenuItem(
        _("Embed Videos"),
        reverse("wagtail_embed_videos:index"),
        name="embedvideos",
        icon_name="media",
        order=301,
    )


@hooks.register("insert_editor_js")
def editor_js():
    return format_html(
        """
        <script>
            window.chooserUrls.embedVideoChooser = '{0}';
        </script>
        """,
        reverse("wagtail_embed_videos:chooser"),
    )


# TODO: implement register_embedvideo_feature

# class EmbedVideosSummaryItem(SummaryItem):
#     order = 201
#     template_name = "wagtail_embed_videos/homepage/site_summary_videos.html"

#     def get_context_data(self, parent_context):
#         return {
#             "total_videos": get_embed_video_model().objects.count(),
#         }

#     def is_shown(self):
#         return permission_policy.user_has_any_permission(self.request.user, ["add", "change", "delete"])


# @hooks.register("construct_homepage_summary_items")
# def add_embed_videos_summary_item(request, items):
#     items.append(EmbedVideosSummaryItem(request))


class EmbedVideosSearchArea(SearchArea):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(request.user, ["add", "change", "delete"])


@hooks.register("register_admin_search_area")
def register_embedvideos_search_area():
    return EmbedVideosSearchArea(
        _("Embed Videos"),
        reverse("wagtail_embed_videos:index"),
        name="embedvideos",
        classnames="icon icon-media",
        order=201,
    )


@hooks.register("register_group_permission_panel")
def register_embedvideo_permissions_panel():
    return GroupEmbedVideoPermissionFormSet


@hooks.register("describe_collection_contents")
def describe_collection_docs(collection):
    embedvideos_count = get_embed_video_model().objects.filter(collection=collection).count()
    if embedvideos_count:
        url = reverse("wagtail_embed_videos:index") + ("?collection_id=%d" % collection.id)
        return {
            "count": embedvideos_count,
            "count_text": ngettext("%(count)s embed video", "%(count)s embed videos", embedvideos_count)
            % {"count": embedvideos_count},
            "url": url,
        }


class EmbedVideoAdminURLFinder(ModelAdminURLFinder):
    edit_url_name = 'wagtail_embed_videos:edit'
    permission_policy = permission_policy

register_admin_url_finder(get_embed_video_model(), EmbedVideoAdminURLFinder)


for action_class in [AddTagsBulkAction, AddToCollectionBulkAction, DeleteBulkAction]:
    hooks.register('register_bulk_action', action_class)
