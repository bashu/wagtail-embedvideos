from django.conf.urls import url

from wagtail_embed_videos.views import embed_videos, chooser


urlpatterns = [
    url(r'^$', embed_videos.index, name='wagtail_embed_videos_index'),
    url(r'^(\d+)/$', embed_videos.edit, name='wagtail_embed_videos_edit_embed_video'),
    url(r'^(\d+)/delete/$', embed_videos.delete, name='wagtail_embed_videos_delete_embed_video'),
    url(r'^(\d+)/preview/(.*)/$', embed_videos.preview, name='wagtail_embed_videos_preview'),
    url(r'^add/$', embed_videos.add, name='wagtail_embed_videos_add_embed_video'),
    url(r'^usage/(\d+)/$', embed_videos.usage, name='wagtail_embed_videos_video_usage'),

    url(r'^chooser/$', chooser.chooser, name='wagtail_embed_videos_chooser'),
    url(r'^chooser/(\d+)/$', chooser.embed_video_chosen, name='wagtail_embed_videos_embed_video_chosen'),
    # url(r'^chooser/upload/$', chooser.chooser_upload, name='wagtail_embed_videos_chooser_upload'),
    # url(r'^chooser/(\d+)/select_format/$', chooser.chooser_select_format, name='wagtail_embed_videos_chooser_select_format'),
]
