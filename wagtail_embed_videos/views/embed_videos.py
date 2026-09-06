# ruff: noqa: N806
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.http import urlencode
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.utils.translation import ngettext

from wagtail.admin import messages
from wagtail.admin.auth import PermissionPolicyChecker
from wagtail.admin.filters import BaseMediaFilterSet
from wagtail.admin.utils import get_valid_next_url_from_request
from wagtail.admin.utils import set_query_params
from wagtail.admin.views import generic

from wagtail_embed_videos import get_embed_video_model
from wagtail_embed_videos.forms import get_embed_video_form
from wagtail_embed_videos.permissions import permission_policy

permission_checker = PermissionPolicyChecker(permission_policy)

EmbedVideo = get_embed_video_model()

USAGE_PAGE_SIZE = getattr(settings, "WAGTAILEMBEDVIDEOS_USAGE_PAGE_SIZE", 20)


class EmbedVideosFilterSet(BaseMediaFilterSet):
    permission_policy = permission_policy

    class Meta:
        model = EmbedVideo
        fields = []


class IndexView(generic.IndexView):
    ORDERING_OPTIONS = {
        "-created_at": gettext_lazy("Newest"),
        "created_at": gettext_lazy("Oldest"),
    }
    default_ordering = "-created_at"
    context_object_name = "embed_videos"
    permission_policy = permission_policy
    any_permission_required = ["add", "change", "delete"]
    model = EmbedVideo
    filterset_class = EmbedVideosFilterSet
    show_other_searches = True
    header_icon = "media"
    page_title = gettext_lazy("Embed Videos")
    add_item_label = gettext_lazy("Add embed video")
    index_url_name = "wagtail_embed_videos:index"
    index_results_url_name = "wagtail_embed_videos:index_results"
    add_url_name = "wagtail_embed_videos:add"
    edit_url_name = "wagtail_embed_videos:edit"
    _show_breadcrumbs = True
    template_name = "wagtail_embed_videos/embed_videos/index.html"
    results_template_name = "wagtail_embed_videos/embed_videos/index_results.html"
    columns = []

    def get_paginate_by(self, queryset):
        return getattr(settings, "WAGTAILEMBEDVIDEOS_INDEX_PAGE_SIZE", 30)

    def get_valid_orderings(self):
        return self.ORDERING_OPTIONS

    def get_base_queryset(self):
        # Get embed videos (filtered by user permission)
        return permission_policy.instances_user_has_any_permission_for(
            self.request.user,
            ["change", "delete"],
        ).select_related("collection")

    @cached_property
    def current_collection(self):
        # Upon validation, the cleaned data is a Collection instance
        return self.filters and self.filters.form.cleaned_data.get("collection_id")

    def get_add_url(self):
        # Pass the collection filter to prefill the add form's collection field
        return set_query_params(
            super().get_add_url(),
            {"collection_id": self.current_collection and self.current_collection.pk},
        )

    def get_filterset_kwargs(self):
        kwargs = super().get_filterset_kwargs()
        kwargs["is_searching"] = self.is_searching
        return kwargs

    def get_next_url(self):
        next_url = self.index_url
        request_query_string = self.request.META.get("QUERY_STRING")
        if request_query_string:
            next_url += "?" + request_query_string
        return next_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "next": self.get_next_url(),
                "current_collection": self.current_collection,
                "current_ordering": self.ordering,
                "ORDERING_OPTIONS": self.ORDERING_OPTIONS,
            },
        )

        return context


@permission_checker.require("change")
def edit(request, embed_video_id):
    EmbedVideo = get_embed_video_model()
    EmbedVideoForm = get_embed_video_form(EmbedVideo)

    embed_video = get_object_or_404(EmbedVideo, id=embed_video_id)

    if not permission_policy.user_has_permission_for_instance(
        request.user,
        "change",
        embed_video,
    ):
        raise PermissionDenied

    next_url = get_valid_next_url_from_request(request)

    if request.method == "POST":
        form = EmbedVideoForm(
            request.POST,
            request.FILES,
            instance=embed_video,
            user=request.user,
        )
        if form.is_valid():
            form.save()

            edit_url = reverse("wagtail_embed_videos:edit", args=(embed_video.id,))
            redirect_url = "wagtail_embed_videos:index"
            if next_url:
                edit_url = f"{edit_url}?{urlencode({'next': next_url})}"
                redirect_url = next_url

            messages.success(
                request,
                _("Video '{0}' updated.").format(embed_video.title),
                buttons=[
                    messages.button(edit_url, _("Edit again")),
                ],
            )
            return redirect(redirect_url)
        messages.error(request, _("The video could not be saved due to errors."))
    else:
        form = EmbedVideoForm(instance=embed_video, user=request.user)

    return TemplateResponse(
        request,
        "wagtail_embed_videos/embed_videos/edit.html",
        {
            "embed_video": embed_video,
            "form": form,
            "user_can_delete": permission_policy.user_has_permission_for_instance(
                request.user,
                "delete",
                embed_video,
            ),
            "next": next_url,
        },
    )


class DeleteView(generic.DeleteView):
    model = get_embed_video_model()
    pk_url_kwarg = "embed_video_id"
    permission_policy = permission_policy
    permission_required = "delete"
    header_icon = "media"
    template_name = "wagtail_embed_videos/embed_videos/confirm_delete.html"
    usage_url_name = "wagtail_embed_videos:embed_video_usage"
    delete_url_name = "wagtail_embed_videos:delete"
    index_url_name = "wagtail_embed_videos:index"
    page_title = gettext_lazy("Delete embed video")

    def user_has_permission(self, permission):
        return self.permission_policy.user_has_permission_for_instance(
            self.request.user,
            permission,
            self.object,
        )

    @property
    def confirmation_message(self):
        # This message will only appear in the singular, but we specify a plural
        # so it can share the translation string with confirm_bulk_delete.html
        return ngettext(
            "Are you sure you want to delete this embed video?",
            "Are you sure you want to delete these embed videos?",
            1,
        )

    def get_success_message(self):
        return _("Video '%(embed_video_title)s' deleted.") % {
            "embed_video_title": self.object.title,
        }


@permission_checker.require("add")
def add(request):
    EmbedVideo = get_embed_video_model()
    EmbedVideoForm = get_embed_video_form(EmbedVideo)

    if request.method == "POST":
        embed_video = EmbedVideo(uploaded_by_user=request.user)
        form = EmbedVideoForm(
            request.POST,
            request.FILES,
            instance=embed_video,
            user=request.user,
        )
        if form.is_valid():
            form.save()

            messages.success(
                request,
                _("Video '{0}' added.").format(embed_video.title),
                buttons=[
                    messages.button(
                        reverse("wagtail_embed_videos:edit", args=(embed_video.id,)),
                        _("Edit"),
                    ),
                ],
            )
            return redirect("wagtail_embed_videos:index")
        messages.error(request, _("The video could not be created due to errors."))
    else:
        form = EmbedVideoForm(user=request.user)

    return TemplateResponse(
        request,
        "wagtail_embed_videos/embed_videos/add.html",
        {
            "form": form,
        },
    )


class UsageView(generic.UsageView):
    model = get_embed_video_model()
    paginate_by = USAGE_PAGE_SIZE
    pk_url_kwarg = "embed_video_id"
    permission_policy = permission_policy
    permission_required = "change"
    header_icon = "media"

    def user_has_permission(self, permission):
        return self.permission_policy.user_has_permission_for_instance(
            self.request.user,
            permission,
            self.object,
        )

    def get_page_subtitle(self):
        return self.object.title
