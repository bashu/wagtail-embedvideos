import json

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.vary import vary_on_headers
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from wagtail.utils.pagination import paginate
from wagtail.wagtailadmin.forms import SearchForm
from wagtail.wagtailadmin import messages
from wagtail.wagtailadmin.utils import PermissionPolicyChecker
from wagtail.wagtailadmin.utils import permission_denied
from wagtail.wagtailadmin.utils import popular_tags_for_model
from wagtail.wagtailcore.models import Collection
from wagtail.wagtailsearch import index as search_index

from wagtail_embed_videos import get_embed_video_model
from wagtail_embed_videos.forms import get_embed_video_form
from wagtail_embed_videos.permissions import permission_policy

permission_checker = PermissionPolicyChecker(permission_policy)


@permission_checker.require_any('add', 'change', 'delete')
@vary_on_headers('X-Requested-With')
def index(request):
    EmbedVideo = get_embed_video_model()

    # Get embed videos
    embed_videos = permission_policy.instances_user_has_any_permission_for(
        request.user, ['change', 'delete']
    ).order_by('-created_at')

    # Search
    query_string = None
    if 'q' in request.GET:
        form = SearchForm(request.GET, placeholder=_("Search videos"))
        if form.is_valid():
            query_string = form.cleaned_data['q']

            embed_videos = embed_videos.search(query_string)
    else:
        form = SearchForm(placeholder=_("Search videos"))

    # Filter by collection
    current_collection = None
    collection_id = request.GET.get('collection_id')
    if collection_id:
        try:
            current_collection = Collection.objects.get(id=collection_id)
            embed_videos = embed_videos.filter(collection=current_collection)
        except (ValueError, Collection.DoesNotExist):
            pass

    # Pagination
    paginator, embed_videos = paginate(request, embed_videos)

    collections = permission_policy.collections_user_has_any_permission_for(
        request.user, ['add', 'change']
    )
    if len(collections) < 2:
        collections = None

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
                'popular_tags': popular_tags_for_model(EmbedVideo),
                'collections': collections,
                'current_collection': current_collection,
                'user_can_add': permission_policy.user_has_permission(request.user, 'add'),
            }
        )


@permission_checker.require('change')
def edit(request, embed_video_id):
    EmbedVideo = get_embed_video_model()
    EmbedVideoForm = get_embed_video_form(EmbedVideo)

    embed_video = get_object_or_404(EmbedVideo, id=embed_video_id)

    if not permission_policy.user_has_permission_for_instance(request.user, 'change', embed_video):
        return permission_denied(request)

    if request.method == 'POST':
        form = EmbedVideoForm(request.POST, request.FILES, instance=embed_video, user=request.user)
        if form.is_valid():
            form.save()

            # Reindex the embed video to make sure all tags are indexed
            search_index.insert_or_update_object(embed_video)

            messages.success(
                request,
                _("Video '{0}' updated.").format(embed_video.title), buttons=[
                    messages.button(
                        reverse(
                            'wagtail_embed_videos:edit',
                            args=(embed_video.id,)
                        ),
                        _('Edit again')
                    )
                ]
            )
            return redirect('wagtail_embed_videos:index')
        else:
            messages.error(request, _("The video could not be saved due to errors."))
    else:
        form = EmbedVideoForm(instance=embed_video, user=request.user)

    return render(request, "wagtail_embed_videos/embed_videos/edit.html", {
        'embed_video': embed_video,
        'form': form,
        'user_can_delete': permission_policy.user_has_permission_for_instance(
            request.user, 'delete', embed_video
        ),
    })


def json_response(document, status=200):
    return HttpResponse(json.dumps(document), content_type='application/json', status=status)


def preview(request, embed_video_id):
    embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)

    return HttpResponse({'embed_video_preview': embed_video.url.thumbnail}, content_type='image/jpeg')


@permission_checker.require('delete')
def delete(request, embed_video_id):
    embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)

    if not permission_policy.user_has_permission_for_instance(request.user, 'delete', embed_video):
        return permission_denied(request)

    if request.method == 'POST':
        embed_video.delete()
        messages.success(request, _("Video '{0}' deleted.").format(embed_video.title))
        return redirect('wagtail_embed_videos:index')

    return render(request, "wagtail_embed_videos/embed_videos/confirm_delete.html", {
        'embed_video': embed_video,
    })


@permission_checker.require('add')
def add(request):
    EmbedVideoModel = get_embed_video_model()
    EmbedVideoForm = get_embed_video_form(EmbedVideoModel)

    if request.method == 'POST':
        embed_video = EmbedVideoModel(uploaded_by_user=request.user)
        form = EmbedVideoForm(request.POST, request.FILES, instance=embed_video, user=request.user)
        if form.is_valid():
            form.save()

            # Reindex the embed video to make sure all tags are indexed
            search_index.insert_or_update_object(embed_video)

            messages.success(
                request,
                _("Video '{0}' added.").format(embed_video.title),
                buttons=[
                    messages.button(
                        reverse(
                            'wagtail_embed_videos:edit',
                            args=(embed_video.id,)
                        ),
                        _('Edit')
                    )
                ]
            )
            return redirect('wagtail_embed_videos:index')
        else:
            messages.error(request, _("The video could not be created due to errors."))
    else:
        form = EmbedVideoForm(user=request.user)

    return render(request, "wagtail_embed_videos/embed_videos/add.html", {
        'form': form,
    })


def usage(request, embed_video_id):
    embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)

    # Pagination
    paginator, used_by = paginate(request, embed_video.get_usage())

    return render(request, "wagtail_embed_videos/embed_videos/usage.html", {
        'embed_video': embed_video,
        'used_by': used_by
    })
