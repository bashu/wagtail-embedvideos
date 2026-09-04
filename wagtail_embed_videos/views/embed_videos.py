# ruff: noqa: N806
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.utils.translation import ngettext
from django.views.generic import TemplateView

from wagtail.admin import messages
from wagtail.admin.auth import PermissionPolicyChecker
from wagtail.admin.forms.search import SearchForm
from wagtail.admin.models import popular_tags_for_model
from wagtail.admin.utils import get_valid_next_url_from_request
from wagtail.admin.views import generic
from wagtail.models import Collection
from wagtail.search.backends import get_search_backend

from wagtail_embed_videos import get_embed_video_model
from wagtail_embed_videos.forms import get_embed_video_form
from wagtail_embed_videos.permissions import permission_policy

permission_checker = PermissionPolicyChecker(permission_policy)

INDEX_PAGE_SIZE = getattr(settings, "WAGTAILEMBEDVIDEOS_INDEX_PAGE_SIZE", 30)
USAGE_PAGE_SIZE = getattr(settings, "WAGTAILEMBEDVIDEOS_USAGE_PAGE_SIZE", 20)


class BaseListingView(TemplateView):
    ENTRIES_PER_PAGE_CHOICES = sorted({10, 30, 60, 100, 250, INDEX_PAGE_SIZE})
    ORDERING_OPTIONS = {
        "-created_at": _("Newest"),
        "created_at": _("Oldest"),
    }
    default_ordering = "-created_at"

    @method_decorator(permission_checker.require_any("add", "change", "delete"))
    def get(self, request):
        return super().get(request)

    def get_num_entries_per_page(self):
        entries_per_page = self.request.GET.get("entries_per_page", INDEX_PAGE_SIZE)
        try:
            entries_per_page = int(entries_per_page)
        except ValueError:
            entries_per_page = INDEX_PAGE_SIZE
        if entries_per_page not in self.ENTRIES_PER_PAGE_CHOICES:
            entries_per_page = INDEX_PAGE_SIZE

        return entries_per_page

    def get_valid_orderings(self):
        return self.ORDERING_OPTIONS

    def get_ordering(self):
        # TODO: remove this method when this view will be based on the
        # generic model index view from wagtail.admin.views.generic.models.IndexView
        ordering = self.request.GET.get("ordering")
        if ordering is None or ordering not in self.get_valid_orderings():
            ordering = self.default_ordering
        return ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get ordering
        ordering = self.get_ordering()

        # Get embed videos (filtered by user permission and ordered by `ordering`)
        embed_videos = (
            permission_policy.instances_user_has_any_permission_for(
                self.request.user,
                ["change", "delete"],
            )
            .order_by(ordering)
            .select_related("collection")
        )

        # Filter by collection
        self.current_collection = None
        collection_id = self.request.GET.get("collection_id")
        if collection_id:
            try:
                self.current_collection = Collection.objects.get(id=collection_id)
                embed_videos = embed_videos.filter(collection=self.current_collection)
            except (ValueError, Collection.DoesNotExist):
                pass

        # Search
        query_string = None
        if "q" in self.request.GET:
            self.form = SearchForm(
                self.request.GET,
                placeholder=_("Search embed videos"),
            )
            if self.form.is_valid():
                query_string = self.form.cleaned_data["q"]
                if query_string:
                    search_backend = get_search_backend()
                    embed_videos = search_backend.autocomplete(
                        query_string,
                        embed_videos,
                    )
        else:
            self.form = SearchForm(placeholder=_("Search embed videos"))

        # Filter by tag
        self.current_tag = self.request.GET.get("tag")
        if self.current_tag:
            try:
                embed_videos = embed_videos.filter(tags__name=self.current_tag)
            except AttributeError:
                self.current_tag = None

        entries_per_page = self.get_num_entries_per_page()
        paginator = Paginator(embed_videos, per_page=entries_per_page)
        embed_videos = paginator.get_page(self.request.GET.get("p"))

        next_url = reverse("wagtail_embed_videos:index")
        request_query_string = self.request.META.get("QUERY_STRING")
        if request_query_string:
            next_url += "?" + request_query_string

        context.update(
            {
                "embed_videos": embed_videos,
                "query_string": query_string,
                "is_searching": bool(query_string),
                "next": next_url,
                "entries_per_page": entries_per_page,
                "ENTRIES_PER_PAGE_CHOICES": self.ENTRIES_PER_PAGE_CHOICES,
                "current_ordering": ordering,
                "ORDERING_OPTIONS": self.ORDERING_OPTIONS,
            },
        )

        return context


class IndexView(BaseListingView):
    template_name = "wagtail_embed_videos/embed_videos/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        collections = permission_policy.collections_user_has_any_permission_for(
            self.request.user,
            ["add", "change"],
        )
        if len(collections) < 2:  # noqa: PLR2004
            collections = None

        EmbedVideo = get_embed_video_model()

        context.update(
            {
                "search_form": self.form,
                "popular_tags": popular_tags_for_model(get_embed_video_model()),
                "current_tag": self.current_tag,
                "collections": collections,
                "current_collection": self.current_collection,
                "user_can_add": permission_policy.user_has_permission(
                    self.request.user,
                    "add",
                ),
                "app_label": EmbedVideo._meta.app_label,  # noqa: SLF001
                "model_name": EmbedVideo._meta.model_name,  # noqa: SLF001
            },
        )
        return context


class ListingResultsView(BaseListingView):
    template_name = "wagtail_embed_videos/embed_videos/results.html"


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
