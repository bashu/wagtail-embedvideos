from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from embed_video.backends import detect_backend
from wagtail.admin.forms.search import SearchForm
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.admin.models import popular_tags_for_model
# from wagtail.utils.pagination import paginate

from wagtail_embed_videos.models import get_embed_video_model


def get_embed_video_json(embed_video):
    """
    helper function: given an embed video, return the json to pass back to the
    embed video chooser panel
    """
    if embed_video.thumbnail:
        preview_embed_video = embed_video.thumbnail.get_rendition('max-130x100').url
    else:
        preview_embed_video = detect_backend(embed_video.url).get_thumbnail_url()

    return {
        'id': embed_video.id,
        'edit_link': reverse('wagtail_embed_videos_edit_embed_video', args=(embed_video.id,)),
        'title': embed_video.title,
        'preview': {
            'url': preview_embed_video,
        }
    }


def chooser(request):
    EmbedVideo = get_embed_video_model()

    if request.user.has_perm('wagtail_embed_videos.add_embedvideo'):
        can_add = True
    else:
        can_add = False

    q = None
    embed_videos = EmbedVideo.objects.order_by('-created_at')
    if 'q' in request.GET or 'p' in request.GET:
        searchform = SearchForm(request.GET)
        if searchform.is_valid():
            q = searchform.cleaned_data['q']

            embed_videos = embed_videos.search(q)

            is_searching = True

        else:
            is_searching = False
            q = None

        # Pagination
        # paginator, embed_videos = paginate(request, embed_videos, per_page=12) DEPRECATED
        paginator = Paginator(embed_videos, per_page=12)
        embed_videos = paginator.get_page(request.GET.get('p'))

        return render(request, "wagtail_embed_videos/chooser/results.html", {
            'embed_videos': embed_videos,
            'is_searching': is_searching,
            'can_add': can_add,
            'query_string': q,
        })
    else:
        # paginator, embed_videos = paginate(request, embed_videos, per_page=12)
        paginator = Paginator(embed_videos, per_page=12)
        embed_videos = paginator.get_page(request.GET.get('p'))

        searchform = SearchForm()

    return render_modal_workflow(
        request,
        'wagtail_embed_videos/chooser/chooser.html',
        None, #'wagtail_embed_videos/chooser/chooser.js',
        template_vars={
            'embed_videos': embed_videos,
            'searchform': searchform,
            'is_searching': False,
            'can_add': can_add,
            'query_string': q,
            'popular_tags': popular_tags_for_model(EmbedVideo),
        },
        json_data={
            'step': 'chooser',
        }
    )


def embed_video_chosen(request, embed_video_id):
    embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)
    json_data = get_embed_video_json(embed_video)
    json_data['step'] = 'embed_video_chosen'

    return render_modal_workflow(
        request, 
        None, 
        None, #'wagtail_embed_videos/chooser/embed_video_chosen.js',
        json_data=json_data
    )
