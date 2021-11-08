from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from wagtail.admin.auth import PermissionPolicyChecker
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.vary import vary_on_headers
from wagtail.admin import messages
from wagtail.admin.forms.search import SearchForm
from wagtail.admin.models import popular_tags_for_model
from wagtail.core.models import Collection
from wagtail.search import index as search_index

from wagtail_embed_videos import get_embed_video_model
from wagtail_embed_videos.forms import get_embed_video_form
from wagtail_embed_videos.permissions import permission_policy

permission_checker = PermissionPolicyChecker(permission_policy)

INDEX_PAGE_SIZE = getattr(settings, "WAGTAILEMBEDVIDEOS_INDEX_PAGE_SIZE", 20)
USAGE_PAGE_SIZE = getattr(settings, "WAGTAILEMBEDVIDEOS_USAGE_PAGE_SIZE", 20)


@permission_checker.require_any("add", "change", "delete")
@vary_on_headers("X-Requested-With")
def index(request):
    EmbedVideo = get_embed_video_model()

    # Get embed videos (filtered by user permission)
    embed_videos = permission_policy.instances_user_has_any_permission_for(request.user, ["change", "delete"]).order_by(
        "-created_at"
    )

    # Search
    query_string = None
    if "q" in request.GET:
        form = SearchForm(request.GET, placeholder=_("Search embed videos"))
        if form.is_valid():
            query_string = form.cleaned_data["q"]

            embed_videos = embed_videos.search(query_string)
    else:
        form = SearchForm(placeholder=_("Search embed videos"))

    # Filter by collection
    current_collection = None
    collection_id = request.GET.get("collection_id")
    if collection_id:
        try:
            current_collection = Collection.objects.get(id=collection_id)
            embed_videos = embed_videos.filter(collection=current_collection)
        except (ValueError, Collection.DoesNotExist):
            pass

    # Filter by tag
    current_tag = request.GET.get("tag")
    if current_tag:
        try:
            embed_videos = embed_videos.filter(tags__name=current_tag)
        except (AttributeError):
            current_tag = None

    paginator = Paginator(embed_videos, per_page=INDEX_PAGE_SIZE)
    embed_videos = paginator.get_page(request.GET.get("p"))

    collections = permission_policy.collections_user_has_any_permission_for(request.user, ["add", "change"])
    if len(collections) < 2:
        collections = None

    # Create response
    if request.is_ajax():
        return TemplateResponse(
            request,
            "wagtail_embed_videos/embed_videos/results.html",
            {
                "embed_videos": embed_videos,
                "query_string": query_string,
                "is_searching": bool(query_string),
            },
        )
    else:
        return TemplateResponse(
            request,
            "wagtail_embed_videos/embed_videos/index.html",
            {
                "embed_videos": embed_videos,
                "query_string": query_string,
                "is_searching": bool(query_string),
                "search_form": form,
                "popular_tags": popular_tags_for_model(EmbedVideo),
                "current_tag": current_tag,
                "collections": collections,
                "current_collection": current_collection,
                "user_can_add": permission_policy.user_has_permission(request.user, "add"),
            },
        )


@permission_checker.require("change")
def edit(request, embed_video_id):
    EmbedVideo = get_embed_video_model()
    EmbedVideoForm = get_embed_video_form(EmbedVideo)

    embed_video = get_object_or_404(EmbedVideo, id=embed_video_id)

    if not permission_policy.user_has_permission_for_instance(request.user, "change", embed_video):
        raise PermissionDenied

    if request.method == "POST":
        form = EmbedVideoForm(request.POST, request.FILES, instance=embed_video, user=request.user)
        if form.is_valid():
            form.save()

            # Reindex the embed video to make sure all tags are indexed
            search_index.insert_or_update_object(embed_video)

            messages.success(
                request,
                _("Video '{0}' updated.").format(embed_video.title),
                buttons=[
                    messages.button(reverse("wagtail_embed_videos:edit", args=(embed_video.id,)), _("Edit again"))
                ],
            )
            return redirect("wagtail_embed_videos:index")
        else:
            messages.error(request, _("The video could not be saved due to errors."))
    else:
        form = EmbedVideoForm(instance=embed_video, user=request.user)

    return TemplateResponse(
        request,
        "wagtail_embed_videos/embed_videos/edit.html",
        {
            "embed_video": embed_video,
            "form": form,
            "user_can_delete": permission_policy.user_has_permission_for_instance(request.user, "delete", embed_video),
        },
    )


@permission_checker.require("delete")
def delete(request, embed_video_id):
    embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)

    if not permission_policy.user_has_permission_for_instance(request.user, "delete", embed_video):
        raise PermissionDenied

    if request.method == "POST":
        embed_video.delete()
        messages.success(request, _("Video '{0}' deleted.").format(embed_video.title))
        return redirect("wagtail_embed_videos:index")

    return TemplateResponse(
        request,
        "wagtail_embed_videos/embed_videos/confirm_delete.html",
        {
            "embed_video": embed_video,
        },
    )


@permission_checker.require("add")
def add(request):
    EmbedVideo = get_embed_video_model()
    EmbedVideoForm = get_embed_video_form(EmbedVideo)

    if request.method == "POST":
        embed_video = EmbedVideo(uploaded_by_user=request.user)
        form = EmbedVideoForm(request.POST, request.FILES, instance=embed_video, user=request.user)
        if form.is_valid():
            form.save()

            # Reindex the embed video to make sure all tags are indexed
            search_index.insert_or_update_object(embed_video)

            messages.success(
                request,
                _("Video '{0}' added.").format(embed_video.title),
                buttons=[messages.button(reverse("wagtail_embed_videos:edit", args=(embed_video.id,)), _("Edit"))],
            )
            return redirect("wagtail_embed_videos:index")
        else:
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


def usage(request, embed_video_id):
    embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)

    paginator = Paginator(embed_video.get_usage(), per_page=USAGE_PAGE_SIZE)
    used_by = paginator.get_page(request.GET.get("p"))

    return TemplateResponse(
        request, "wagtail_embed_videos/embed_videos/usage.html", {"embed_video": embed_video, "used_by": used_by}
    )
