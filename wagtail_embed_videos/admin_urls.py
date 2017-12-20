from django.conf.urls import url

from wagtail_embed_videos.views import chooser
from wagtail_embed_videos.views import embed_videos

# TODO: Delete comment lines, embed_videos only get a url, not upload files.
# from wagtail_embed_videos.views import multiple

urlpatterns = [
    url(r'^$', embed_videos.index, name='index'),
    url(r'^(\d+)/$', embed_videos.edit, name='edit'),
    url(r'^(\d+)/delete/$', embed_videos.delete, name='delete'),
    # url(r'^(\d+)/generate_url/$', embed_videos.url_generator, name='url_generator'),
    # url(r'^(\d+)/generate_url/(.*)/$', embed_videos.generate_url, name='generate_url'),
    url(r'^(\d+)/preview/(.*)/$', embed_videos.preview, name='preview'),
    url(r'^add/$', embed_videos.add, name='add'),
    url(r'^usage/(\d+)/$', embed_videos.usage, name='video_usage'),

    # url(r'^multiple/add/$', multiple.add, name='add_multiple'),
    # url(r'^multiple/(\d+)/$', multiple.edit, name='edit_multiple'),
    # url(r'^multiple/(\d+)/delete/$', multiple.delete, name='delete_multiple'),

    url(r'^chooser/$', chooser.chooser, name='chooser'),
    url(r'^chooser/(\d+)/$', chooser.embed_video_chosen, name='embed_video_chosen'),
    url(r'^chooser/upload/$', chooser.chooser_upload, name='chooser_upload'),
    # url(r'^chooser/(\d+)/select_format/$', chooser.chooser_select_format, name='chooser_select_format'),
]
