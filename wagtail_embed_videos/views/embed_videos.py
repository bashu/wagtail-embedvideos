import json

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from django.views.decorators.vary import vary_on_headers
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from wagtail.wagtailadmin.forms import SearchForm
from wagtail.wagtailadmin import messages
from wagtail.wagtailsearch.backends import get_search_backends

from wagtail_embed_videos.models import get_embed_video_model
from wagtail_embed_videos.forms import get_embed_video_form


@permission_required('wagtail_embed_videos.add_embedvideo')
@vary_on_headers('X-Requested-With')
def index(request):
    EmbedVideo = get_embed_video_model()

    # Get embed videos
    embed_videos = EmbedVideo.objects.order_by('-created_at')

    # Permissions
    if not request.user.has_perm('wagtail_embed_videos.change_embedvideo'):
        # restrict to the user's own embed videos
        embed_videos = embed_videos.filter(uploaded_by_user=request.user)

    # Search
    query_string = None
    if 'q' in request.GET:
        form = SearchForm(request.GET, placeholder=_("Search videos"))
        if form.is_valid():
            query_string = form.cleaned_data['q']

            if not request.user.has_perm(
                'wagtail_embed_videos.change_embedvideo'
            ):
                # restrict to the user's own embed videos
                embed_videos = EmbedVideo.search(
                    query_string,
                    filters={'uploaded_by_user_id': request.user.id}
                )
            else:
                embed_videos = EmbedVideo.search(query_string)
    else:
        form = SearchForm(placeholder=_("Search videos"))

    # Pagination
    p = request.GET.get('p', 1)
    paginator = Paginator(embed_videos, 20)

    try:
        embed_videos = paginator.page(p)
    except PageNotAnInteger:
        embed_videos = paginator.page(1)
    except EmptyPage:
        embed_videos = paginator.page(paginator.num_pages)

    # Create response
    if request.is_ajax():
        return render(
            request,
            'wagtail_embed_videos/embed_videos/results.html',
            {
                'embed_videos': embed_videos,
                'query_string': query_string,
                'is_searching': bool(query_string),
            }
        )
    else:
        return render(
            request,
            'wagtail_embed_videos/embed_videos/index.html',
            {
                'embed_videos': embed_videos,
                'query_string': query_string,
                'is_searching': bool(query_string),
                'search_form': form,
                'popular_tags': EmbedVideo.popular_tags(),
            }
        )


def edit(request, embed_video_id):
    EmbedVideo = get_embed_video_model()
    EmbedVideoForm = get_embed_video_form(EmbedVideo)

    embed_video = get_object_or_404(EmbedVideo, id=embed_video_id)

    if not embed_video.is_editable_by_user(request.user):
        raise PermissionDenied

    if request.POST:
        form = EmbedVideoForm(request.POST, request.FILES, instance=embed_video)
        if form.is_valid():
            form.save()

            # Reindex the embed_video to make sure all tags are indexed
            for backend in get_search_backends():
                backend.add(embed_video)

            messages.success(request, _("Video '{0}' updated.").format(embed_video.title), buttons=[
                messages.button(reverse('wagtail_embed_videos_edit_embed_video', args=(embed_video.id,)), _('Edit again'))
            ])
            return redirect('wagtail_embed_videos_index')
        else:
            messages.error(request, _("The video could not be saved due to errors."))
    else:
        form = EmbedVideoForm(instance=embed_video)

    return render(request, "wagtail_embed_videos/embed_videos/edit.html", {
        'embed_video': embed_video,
        'form': form,
    })


def json_response(document, status=200):
    return HttpResponse(json.dumps(document), content_type='application/json', status=status)


def preview(request, embed_video_id):
    embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)

    return HttpResponse({'embed_video_preview': embed_video.url.thumbnail}, content_type='image/jpeg')


def delete(request, embed_video_id):
    embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)

    if not embed_video.is_editable_by_user(request.user):
        raise PermissionDenied

    if request.POST:
        embed_video.delete()
        messages.success(request, _("Video '{0}' deleted.").format(embed_video.title))
        return redirect('wagtail_embed_videos_index')

    return render(request, "wagtail_embed_videos/embed_videos/confirm_delete.html", {
        'embed_video': embed_video,
    })


@permission_required('wagtail_embed_videos.add_embedvideo')
def add(request):
    EmbedVideoModel = get_embed_video_model()
    EmbedVideoForm = get_embed_video_form(EmbedVideoModel)

    if request.POST:
        embed_video = EmbedVideoModel(uploaded_by_user=request.user)
        form = EmbedVideoForm(request.POST, request.FILES, instance=embed_video)
        if form.is_valid():
            form.save()

            # Reindex the embed video to make sure all tags are indexed
            for backend in get_search_backends():
                backend.add(embed_video)

            messages.success(request, _("Video '{0}' added.").format(embed_video.title), buttons=[
                messages.button(reverse('wagtail_embed_videos_edit_embed_video', args=(embed_video.id,)), _('Edit'))
            ])
            return redirect('wagtail_embed_videos_index')
        else:
            messages.error(request, _("The video could not be created due to errors."))
    else:
        form = EmbedVideoForm()

    return render(request, "wagtail_embed_videos/embed_videos/add.html", {
        'form': form,
    })


def usage(request, embed_video_id):
    embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)

    # Pagination
    p = request.GET.get('p', 1)
    paginator = Paginator(embed_video.get_usage(), 20)

    try:
        used_by = paginator.page(p)
    except PageNotAnInteger:
        used_by = paginator.page(1)
    except EmptyPage:
        used_by = paginator.page(paginator.num_pages)

    return render(request, "wagtail_embed_videos/embed_videos/usage.html", {
        'embed_video': embed_video,
        'used_by': used_by
    })
