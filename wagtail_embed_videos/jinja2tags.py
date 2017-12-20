from jinja2.ext import Extension


def embed_video(embed_video, thumbnail):
    if not embed_video:
        return ''

    if thumbnail:
        return embed_video.thumbnail
    else:
        return embed_video


class WagtailEmbedVideosExtension(Extension):
    def __init__(self, environment):
        super(WagtailEmbedVideosExtension, self).__init__(environment)

        self.environment.globals.update({
            'embed_video': embed_video,
        })


# Nicer import names
embed_videos = WagtailEmbedVideosExtension
