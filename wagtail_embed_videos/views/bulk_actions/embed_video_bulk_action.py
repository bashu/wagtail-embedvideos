from wagtail.admin.views.bulk_action import BulkAction
from wagtail_embed_videos import get_embed_video_model
from wagtail_embed_videos.permissions import permission_policy as embed_videos_permission_policy


class EmbedVideoBulkAction(BulkAction):
    permission_policy = embed_videos_permission_policy
    models = [get_embed_video_model()]

    def get_all_objects_in_listing_query(self, parent_id):
        listing_objects = self.model.objects.all()
        if parent_id is not None:
            listing_objects = listing_objects.filter(collection_id=parent_id)

        listing_objects = listing_objects.values_list('pk', flat=True)

        if 'q' in self.request.GET:
            query_string = self.request.GET.get('q', '')
            listing_objects = listing_objects.search(query_string).results()

        return listing_objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items_with_no_access'] = [
            {
                'item': embed_video,
                'can_edit': self.permission_policy.user_has_permission_for_instance(self.request.user, 'change', embed_video)
            } for embed_video in context['items_with_no_access']
        ]
        return context
