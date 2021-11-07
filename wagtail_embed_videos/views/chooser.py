from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from embed_video.backends import detect_backend
from wagtail.admin.forms.search import SearchForm
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.admin.auth import PermissionPolicyChecker
from wagtail.admin.models import popular_tags_for_model
from wagtail.core import hooks
from wagtail.core.models import Collection
from wagtail.search import index as search_index

from wagtail_embed_videos import get_embed_video_model
from wagtail_embed_videos.forms import get_embed_video_form
from wagtail_embed_videos.permissions import permission_policy

permission_checker = PermissionPolicyChecker(permission_policy)

CHOOSER_PAGE_SIZE = getattr(settings, "WAGTAILEMBEDVIDEOS_CHOOSER_PAGE_SIZE", 12)


def get_chooser_js_data():
    """construct context variables needed by the chooser JS"""
    return {
        "step": "chooser",
        "error_label": _("Server Error"),
        "error_message": _("Report this error to your webmaster with the following information:"),
        "tag_autocomplete_url": reverse("wagtailadmin_tag_autocomplete"),
    }


def get_embed_video_result_data(embed_video):
    """
    helper function: given embed video, return the json data to pass back to the
    embed video chooser panel
    """
    if embed_video.thumbnail:
        preview_url = embed_video.thumbnail.get_rendition("max-165x165").url
    else:
        preview_url = detect_backend(embed_video.url).get_thumbnail_url()

    return {
        "id": embed_video.id,
        "edit_link": reverse("wagtail_embed_videos:edit", args=(embed_video.id,)),
        "title": embed_video.title,
        "preview": {
            "url": preview_url,
        },
    }


def get_chooser_context(request):
    """Helper function to return common template context variables for the main chooser view"""

    collections = Collection.objects.all()
    if len(collections) < 2:
        collections = None
    else:
        collections = Collection.order_for_display(collections)

    return {
        "searchform": SearchForm(),
        "is_searching": False,
        "query_string": None,
        "popular_tags": popular_tags_for_model(get_embed_video_model()),
        "collections": collections,
    }


def chooser(request):
    EmbedVideo = get_embed_video_model()

    if permission_policy.user_has_permission(request.user, "add"):
        EmbedVideoForm = get_embed_video_form(EmbedVideo)
        uploadform = EmbedVideoForm(user=request.user)
    else:
        uploadform = None

    embed_videos = EmbedVideo.objects.order_by("-created_at")

    # allow hooks to modify the queryset
    for hook in hooks.get_hooks("construct_embed_video_chooser_queryset"):
        embed_videos = hook(embed_videos, request)

    if "q" in request.GET or "p" in request.GET or "tag" in request.GET or "collection_id" in request.GET:
        # this request is triggered from search, pagination or 'popular tags';
        # we will just render the results.html fragment
        collection_id = request.GET.get("collection_id")
        if collection_id:
            embed_videos = embed_videos.filter(collection=collection_id)

        searchform = SearchForm(request.GET)
        if searchform.is_valid():
            q = searchform.cleaned_data["q"]

            embed_videos = embed_videos.search(q)
            is_searching = True
        else:
            is_searching = False
            q = None

            tag_name = request.GET.get("tag")
            if tag_name:
                embed_videos = embed_videos.filter(tags__name=tag_name)

        # Pagination
        paginator = Paginator(embed_videos, per_page=CHOOSER_PAGE_SIZE)
        embed_videos = paginator.get_page(request.GET.get("p"))

        return TemplateResponse(
            request,
            "wagtail_embed_videos/chooser/results.html",
            {
                "embed_videos": embed_videos,
                "is_searching": is_searching,
                "query_string": q,
            },
        )
    else:
        paginator = Paginator(embed_videos, per_page=CHOOSER_PAGE_SIZE)
        embed_videos = paginator.get_page(request.GET.get("p"))

        context = get_chooser_context(request)
        context.update(
            {
                "embed_videos": embed_videos,
                "uploadform": uploadform,
            }
        )
        return render_modal_workflow(
            request, "wagtail_embed_videos/chooser/chooser.html", None, context, json_data=get_chooser_js_data()
        )


def embed_video_chosen(request, embed_video_id):
    embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)

    return render_modal_workflow(
        request,
        None,
        None,
        None,
        json_data={"step": "embed_video_chosen", "result": get_embed_video_result_data(embed_video)},
    )


@permission_checker.require("add")
def chooser_upload(request):
    EmbedVideo = get_embed_video_model()
    EmbedVideoForm = get_embed_video_form(EmbedVideo)

    if request.method == "POST":
        embed_video = EmbedVideo(uploaded_by_user=request.user)
        form = EmbedVideoForm(
            request.POST, request.FILES, instance=embed_video, user=request.user, prefix="embed_video-chooser-upload"
        )

        if form.is_valid():
            form.save()

            # Reindex the embed video to make sure all tags are indexed
            search_index.insert_or_update_object(embed_video)

            return render_modal_workflow(
                request,
                None,
                None,
                None,
                json_data={"step": "embed_video_chosen", "result": get_embed_video_result_data(embed_video)},
            )
    else:
        form = EmbedVideoForm(user=request.user, prefix="embed_video-chooser-upload")

    embed_videos = EmbedVideo.objects.order_by("-created_at")

    # allow hooks to modify the queryset
    for hook in hooks.get_hooks("construct_embed_video_chooser_queryset"):
        embed_videos = hook(embed_videos, request)

    paginator = Paginator(embed_videos, per_page=CHOOSER_PAGE_SIZE)
    embed_videos = paginator.get_page(request.GET.get("p"))

    context = get_chooser_context(request)
    context.update(
        {
            "embed_videos": embed_videos,
            "uploadform": form,
        }
    )
    return render_modal_workflow(
        request, "wagtail_embed_videos/chooser/chooser.html", None, context, json_data=get_chooser_js_data()
    )
