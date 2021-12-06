from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from wagtail.admin import widgets
from wagtail_embed_videos.views.bulk_actions.embed_video_bulk_action import EmbedVideoBulkAction


class TagForm(forms.Form):
    tags = forms.Field(widget=widgets.AdminTagWidget)


class AddTagsBulkAction(EmbedVideoBulkAction):
    display_name = _("Tag")
    action_type = "add_tags"
    aria_label = _("Add tags to the selected embed videos")
    template_name = "wagtail_embed_videos/bulk_actions/confirm_bulk_add_tags.html"
    action_priority = 20
    form_class = TagForm

    def check_perm(self, embed_video):
        return self.permission_policy.user_has_permission_for_instance(self.request.user, 'change', embed_video)

    def get_execution_context(self):
        return {
            'tags': self.cleaned_form.cleaned_data['tags'].split(',')
        }

    @classmethod
    def execute_action(cls, embed_videos, tags=[], **kwargs):
        num_parent_objects = 0
        if not tags:
            return
        for embed_video in embed_videos:
            num_parent_objects += 1
            embed_video.tags.add(*tags)
        return num_parent_objects, 0

    def get_success_message(self, num_parent_objects, num_child_objects):
        return ngettext(
            "New tags have been added to %(num_parent_objects)d embed video",
            "New tags have been added to %(num_parent_objects)d embed videos",
            num_parent_objects
        ) % {
            'num_parent_objects': num_parent_objects
        }
