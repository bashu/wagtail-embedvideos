from django.conf import settings
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import View

from embed_video.backends import detect_backend
from wagtail.admin.models import popular_tags_for_model
from wagtail.admin.views.generic.chooser import BaseChooseView
from wagtail.admin.views.generic.chooser import ChooseResultsViewMixin
from wagtail.admin.views.generic.chooser import ChooseViewMixin
from wagtail.admin.views.generic.chooser import ChosenMultipleViewMixin
from wagtail.admin.views.generic.chooser import ChosenResponseMixin
from wagtail.admin.views.generic.chooser import ChosenViewMixin
from wagtail.admin.views.generic.chooser import CreateViewMixin
from wagtail.admin.views.generic.chooser import CreationFormMixin
from wagtail.admin.viewsets.chooser import ChooserViewSet

from wagtail_embed_videos import get_embed_video_model
from wagtail_embed_videos.forms import get_embed_video_form
from wagtail_embed_videos.permissions import permission_policy


class EmbedVideoChosenResponseMixin(ChosenResponseMixin):
    def get_chosen_response_data(
        self,
        embed_video,
        preview_image_filter="max-165x165",
    ):
        """
        Given an embed video, return the json data to pass back to the embed
        video chooser panel
        """
        response_data = super().get_chosen_response_data(embed_video)
        if embed_video.thumbnail:
            preview_image = embed_video.thumbnail.get_rendition(preview_image_filter)
            preview = {
                "url": preview_image.url,
                "width": preview_image.width,
                "height": preview_image.height,
            }
        else:
            preview = {
                "url": detect_backend(embed_video.url).get_thumbnail_url(),
                "width": 165,
                "height": 92,
            }
        response_data["preview"] = preview
        return response_data


class EmbedVideoCreationFormMixin(CreationFormMixin):
    creation_tab_id = "upload"
    create_action_label = _("Upload")
    create_action_clicked_label = _("Uploading…")
    permission_policy = permission_policy

    def get_creation_form_class(self):
        return get_embed_video_form(self.model)

    def get_creation_form_kwargs(self):
        kwargs = super().get_creation_form_kwargs()
        kwargs.update(
            {
                "user": self.request.user,
                "prefix": "embed_video-chooser-upload",
            },
        )
        if self.request.method in ("POST", "PUT"):
            kwargs["instance"] = self.model(uploaded_by_user=self.request.user)
        return kwargs


class BaseEmbedVideoChooseView(BaseChooseView):
    template_name = "wagtail_embed_videos/chooser/chooser.html"
    results_template_name = "wagtail_embed_videos/chooser/results.html"
    per_page = getattr(settings, "WAGTAILEMBEDVIDEOS_CHOOSER_PAGE_SIZE", 12)
    ordering = "-created_at"
    construct_queryset_hook_name = "construct_embed_video_chooser_queryset"
    icon = "media"

    def get_object_list(self):
        return permission_policy.instances_user_has_any_permission_for(
            self.request.user,
            ["choose"],
        ).select_related("collection")

    def filter_object_list(self, objects):
        tag_name = self.request.GET.get("tag")
        if tag_name:
            objects = objects.filter(tags__name=tag_name)
        return super().filter_object_list(objects)

    def get_filter_form(self):
        FilterForm = self.get_filter_form_class()  # noqa: N806
        return FilterForm(self.request.GET, collections=self.collections)

    @cached_property
    def collections(self):
        collections = permission_policy.collections_user_has_permission_for(
            self.request.user,
            "choose",
        )
        if len(collections) < 2:  # noqa: PLR2004
            return None
        return collections

    def get(self, request):
        self.model = get_embed_video_model()
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for embed_video in context["results"]:
            embed_video.chosen_url = self.append_preserved_url_parameters(
                reverse("wagtail_embed_videos_chooser:chosen", args=(embed_video.id,)),
            )
        context["collections"] = self.collections
        return context


class EmbedVideoChooseViewMixin(ChooseViewMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["popular_tags"] = popular_tags_for_model(self.model_class)
        return context

    def get_response_json_data(self):
        json_data = super().get_response_json_data()
        json_data["tag_autocomplete_url"] = reverse("wagtailadmin_tag_autocomplete")
        return json_data


class EmbedVideoChooseView(
    EmbedVideoChooseViewMixin,
    EmbedVideoCreationFormMixin,
    BaseEmbedVideoChooseView,
):
    pass


class EmbedVideoChooseResultsView(
    ChooseResultsViewMixin,
    EmbedVideoCreationFormMixin,
    BaseEmbedVideoChooseView,
):
    pass


class EmbedVideoChosenView(ChosenViewMixin, EmbedVideoChosenResponseMixin, View):
    def get(self, request, *args, pk, **kwargs):
        self.model = get_embed_video_model()
        return super().get(request, *args, pk, **kwargs)


class EmbedVideoChosenMultipleView(
    ChosenMultipleViewMixin,
    EmbedVideoChosenResponseMixin,
    View,
):
    def get(self, request, *args, **kwargs):
        self.model = get_embed_video_model()
        return super().get(request, *args, **kwargs)


class EmbedVideoCreateView(
    CreateViewMixin,
    EmbedVideoCreationFormMixin,
    EmbedVideoChosenResponseMixin,
    View,
):
    def get(self, request):
        self.model = get_embed_video_model()
        return super().get(request)

    def post(self, request):
        self.model = get_embed_video_model()
        return super().post(request)


class EmbedVideoChooserViewSet(ChooserViewSet):
    choose_view_class = EmbedVideoChooseView
    choose_results_view_class = EmbedVideoChooseResultsView
    chosen_view_class = EmbedVideoChosenView
    chosen_multiple_view_class = EmbedVideoChosenMultipleView
    create_view_class = EmbedVideoCreateView
    permission_policy = permission_policy
    # We register our own explicit AdminEmbedVideoChooser widget (with thumbnail
    # preview support) via apps.py instead of the viewset's auto-generated one.
    register_widget = False
    preserve_url_parameters = ChooserViewSet.preserve_url_parameters

    icon = "media"
    choose_one_text = _("Choose an embed video")
    choose_another_text = _("Choose another embed video")
    edit_item_text = _("Edit this embed video")
    create_action_label = _("Upload")
    create_action_clicked_label = _("Uploading…")


viewset = EmbedVideoChooserViewSet(
    "wagtail_embed_videos_chooser",
    model=get_embed_video_model(),
    url_prefix="embed-videos/chooser",
)
