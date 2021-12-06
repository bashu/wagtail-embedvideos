from types import SimpleNamespace

from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic.base import View
from embed_video.backends import detect_backend
from wagtail.admin.auth import PermissionPolicyChecker
from wagtail.admin.forms.search import SearchForm
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.admin.models import popular_tags_for_model
from wagtail.core import hooks
from wagtail.search import index as search_index

from wagtail_embed_videos import get_embed_video_model
from wagtail_embed_videos.forms import get_embed_video_form
from wagtail_embed_videos.permissions import permission_policy

permission_checker = PermissionPolicyChecker(permission_policy)

CHOOSER_PAGE_SIZE = getattr(settings, "WAGTAILEMBEDVIDEOS_CHOOSER_PAGE_SIZE", 12)


def get_embed_video_result_data(embed_video):
    """
    helper function: given embed video, return the json data to pass back to the
    embed video chooser panel
    """
    if embed_video.thumbnail:
        preview = embed_video.thumbnail.get_rendition("max-165x165")
    else:
        preview = SimpleNamespace(
            url=detect_backend(embed_video.url).get_thumbnail_url(),
            width=165,
            height=92,
        )

    return {
        "id": embed_video.id,
        "edit_link": reverse("wagtail_embed_videos:edit", args=(embed_video.id,)),
        "title": embed_video.title,
        "preview": {
            "url": preview.url,
            "width": preview.width,
            "height": preview.height,
        },
    }


class BaseChooseView(View):
    def get(self, request):
        self.embed_video_model = get_embed_video_model()

        embed_videos = permission_policy.instances_user_has_any_permission_for(request.user, ["choose"]).order_by(
            "-created_at"
        )

        # allow hooks to modify the queryset
        for hook in hooks.get_hooks("construct_embed_video_chooser_queryset"):
            embed_videos = hook(embed_videos, request)

        collection_id = request.GET.get("collection_id")
        if collection_id:
            embed_videos = embed_videos.filter(collection=collection_id)

        self.is_searching = False
        self.q = None

        if 'q' in request.GET:
            self.search_form = SearchForm(request.GET)
            if self.search_form.is_valid():
                self.q = self.search_form.cleaned_data['q']
                self.is_searching = True
                embed_videos = embed_videos.search(self.q)
        else:
            self.search_form = SearchForm()

        if not self.is_searching:
            tag_name = request.GET.get("tag")
            if tag_name:
                embed_videos = embed_videos.filter(tags__name=tag_name)

        # Pagination
        paginator = Paginator(embed_videos, per_page=CHOOSER_PAGE_SIZE)
        self.embed_videos = paginator.get_page(request.GET.get('p'))
        return self.render_to_response()

    def get_context_data(self):
        return {
            'embed_videos': self.embed_videos,
            'is_searching': self.is_searching,
            'query_string': self.q,
        }

    def render_to_response(self):
        raise NotImplementedError()


class ChooseView(BaseChooseView):
    def get_context_data(self):
        context = super().get_context_data()

        if permission_policy.user_has_permission(self.request.user, 'add'):
            EmbedVideoForm = get_embed_video_form(self.embed_video_model)
            uploadform = EmbedVideoForm(user=self.request.user, prefix='embed_video-chooser-upload')
        else:
            uploadform = None

        collections = permission_policy.collections_user_has_permission_for(
            self.request.user, 'choose'
        )
        if len(collections) < 2:
            collections = None

        context.update({
            'searchform': self.search_form,
            'popular_tags': popular_tags_for_model(self.embed_video_model),
            'collections': collections,
            'uploadform': uploadform,
        })
        return context

    def render_to_response(self):
        return render_modal_workflow(
            self.request, 'wagtail_embed_videos/chooser/chooser.html', None, self.get_context_data(),
            json_data={
                'step': 'chooser',
                'error_label': _("Server Error"),
                'error_message': _("Report this error to your webmaster with the following information:"),
                'tag_autocomplete_url': reverse('wagtailadmin_tag_autocomplete'),
            }
        )


class ChooseResultsView(BaseChooseView):
    def render_to_response(self):
        return TemplateResponse(self.request, "wagtail_embed_videos/chooser/results.html", self.get_context_data())


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

    upload_form_html = render_to_string('wagtail_embed_videos/chooser/upload_form.html', {
        'form': form,
    }, request)

    return render_modal_workflow(
        request, None, None, None,
        json_data={
            'step': 'reshow_upload_form',
            'htmlFragment': upload_form_html
        }
    )
