import json

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import permission_required
from wagtail.utils.pagination import paginate

from wagtail.wagtailadmin.modal_workflow import render_modal_workflow
from wagtail.wagtailadmin.forms import SearchForm
from wagtail.wagtailcore.models import Collection
from wagtail.wagtailsearch.backends import get_search_backends

from embed_video.backends import detect_backend

from wagtail_embed_videos.models import get_embed_video_model
from wagtail_embed_videos.forms import get_embed_video_form, EmbedVideoInsertionForm
# from wagtail_embed_videos.formats import get_embed_video_format
from wagtail_embed_videos.permissions import permission_policy


def get_embed_video_json(embed_video):
    """
    helper function: given an embed video, return the json to pass back to the
    embed video chooser panel
    """
    if embed_video.thumbnail:
        preview_embed_video = embed_video.thumbnail.get_rendition('max-130x100').url
    else:
        preview_embed_video = detect_backend(embed_video.url).get_thumbnail_url()

    return json.dumps({
        'id': embed_video.id,
        'edit_link': reverse('wagtail_embed_videos_edit_embed_video', args=(embed_video.id,)),
        'title': embed_video.title,
        'preview': {
            'url': preview_embed_video,
        }
    })


def chooser(request):
    EmbedVideo = get_embed_video_model()

    if permission_policy.user_has_permission(request.user, 'add'):
        EmbedVideoForm = get_embed_video_form(EmbedVideo)
        uploadform = EmbedVideoForm()
        can_add = True
    else:
        uploadform = None
        can_add = False

    embed_videos = EmbedVideo.objects.order_by('-created_at')

    q = None
    if (
                            'q' in request.GET or 'p' in request.GET or 'tag' in request.GET or
                    'collection_id' in request.GET
    ):
        collection_id = request.GET.get('collection_id')
        if collection_id:
            embed_videos = embed_videos.filter(collection=collection_id)

        searchform = SearchForm(request.GET)
        if searchform.is_valid():
            q = searchform.cleaned_data['q']

            embed_videos = embed_videos.search(q)
            is_searching = True

        else:
            is_searching = False

            tag_name = request.GET.get('tag')
            if tag_name:
                embed_videos = embed_videos.filter(tags__name=tag_name)

        paginator, embed_videos = paginate(request, embed_videos, per_page=12)

        return render(request, "wagtail_embed_videos/chooser/results.html", {
            'embed_videos': embed_videos,
            'is_searching': is_searching,
            'can_add': can_add,
            'query_string': q,
            'will_select_format': request.GET.get('select_format')
        })
    else:
        searchform = SearchForm()

        collections = Collection.objects.all()
        if len(collections) < 2:
            collections = None

        paginator, embed_videos = paginate(request, embed_videos, per_page=12)

    return render_modal_workflow(
        request,
        'wagtail_embed_videos/chooser/chooser.html',
        'wagtail_embed_videos/chooser/chooser.js',
        {
            'embed_videos': embed_videos,
            'uploadform': uploadform,
            'searchform': searchform,
            'is_searching': False,
            'can_add': can_add,
            'query_string': q,
            'will_select_format': request.GET.get('select_format'),
            'popular_tags': EmbedVideo.popular_tags(),
            'collections': collections,
        }
    )


def embed_video_chosen(request, embed_video_id):
    embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)

    return render_modal_workflow(
        request, None, 'wagtail_embed_videos/chooser/embed_video_chosen.js',
        {'embed_video_json': get_embed_video_json(embed_video)}
    )

# @permission_required('wagtail_embed_videos.add_embedvideo')
# def chooser_upload(request):
#     EmbedVideo = get_embed_video_model()
#     EmbedVideoForm = get_embed_video_form(EmbedVideo)

#     searchform = SearchForm()

#     if request.POST:
#         embed_video = EmbedVideo(uploaded_by_user=request.user)
#         form = EmbedVideoForm(request.POST, request.FILES, instance=embed_video)

#         if form.is_valid():
#             form.save()

#             # Reindex the embed video to make sure all tags are indexed
#             for backend in get_search_backends():
#                 backend.add(embed_video)

#             if request.GET.get('select_format'):
#                 form = EmbedVideoInsertionForm(initial={'alt_text': embed_video.default_alt_text})
#                 return render_modal_workflow(
#                     request, 'wagtail_embed_videos/chooser/select_format.html', 'wagtail_embed_videos/chooser/select_format.js',
#                     {'embed_video': embed_video, 'form': form}
#                 )
#             else:
#                 # not specifying a format; return the embed video details now
#                 return render_modal_workflow(
#                     request, None, 'wagtail_embed_videos/chooser/embed_video_chosen.js',
#                     {'embed_video_json': get_embed_video_json(embed_video)}
#                 )
#     else:
#         form = EmbedVideoForm()

#     embed_videos = EmbedVideo.objects.order_by('title')

#     return render_modal_workflow(
#         request, 'wagtail_embed_videos/chooser/chooser.html', 'wagtail_embed_videos/chooser/chooser.js',
#         {'embed_videos': embed_videos, 'uploadform': form, 'searchform': searchform}
#     )


# def chooser_select_format(request, embed_video_id):
#     embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)

#     if request.POST:
#         form = EmbedVideoInsertionForm(request.POST, initial={'alt_text': embed_video.default_alt_text})
#         if form.is_valid():

#             preview_embed_video = detect_backend(embed_video.url).get_thumbnail_url()

#             embed_video_json = json.dumps({
#                 'id': embed_video.id,
#                 'title': embed_video.title,
#                 'format': format.name,
#                 'alt': form.cleaned_data['alt_text'],
#                 'class': format.classnames,
#                 'edit_link': reverse('wagtail_embed_videos_edit_embed_video', args=(embed_video.id,)),
#                 'preview': {
#                     'url': preview_embed_video,
#                 },
#                 'html': format.embed_video_to_editor_html(embed_video, form.cleaned_data['alt_text']),
#             })

#             return render_modal_workflow(
#                 request, None, 'wagtail_embed_videos/chooser/embed_video_chosen.js',
#                 {'embed_video_json': embed_video_json}
#             )
#     else:
#         form = EmbedVideoInsertionForm(initial={'alt_text': embed_video.default_alt_text})

#     return render_modal_workflow(
#         request, 'wagtail_embed_videos/chooser/select_format.html', 'wagtail_embed_videos/chooser/select_format.js',
#         {'embed_video': embed_video, 'form': form}
#     )
