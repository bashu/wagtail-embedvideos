from django.conf.urls import url

from wagtail_embed_videos.views import chooser, embed_videos

app_name = "wagtail_embed_videos"

urlpatterns = [
    url(r"^$", embed_videos.index, name="index"),
    url(r"^(\d+)/$", embed_videos.edit, name="edit"),
    url(r"^(\d+)/delete/$", embed_videos.delete, name="delete"),
    url(r"^add/$", embed_videos.add, name="add"),
    url(r"^usage/(\d+)/$", embed_videos.usage, name="embed_video_usage"),
    url(r"^chooser/$", chooser.chooser, name="chooser"),
    url(r"^chooser/(\d+)/$", chooser.embed_video_chosen, name="embed_video_chosen"),
    url(r"^chooser/upload/$", chooser.chooser_upload, name="chooser_upload"),
]
