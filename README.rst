wagtail-embedvideos
===================

.. image:: https://img.shields.io/pypi/v/wagtail-embedvideos.svg
    :target: https://pypi.python.org/pypi/wagtail-embedvideos/

.. image:: https://img.shields.io/pypi/dm/wagtail-embedvideos.svg
    :target: https://pypi.python.org/pypi/wagtail-embedvideos/

.. image:: https://img.shields.io/github/license/bashu/wagtail-embedvideos.svg
    :target: https://pypi.python.org/pypi/wagtail-embedvideos/

.. image:: https://img.shields.io/travis/bashu/wagtail-embedvideos.svg
    :target: https://travis-ci.com/github/bashu/wagtail-embedvideos/

Simple app that works similar to ``wagtailimages``, but for embedding YouTube and Vimeo videos and music from SoundCloud.

The current version is tested for compatiblily with the following:

- Wagtail versions 2.7 to 2.15
- Django versions 2.2 to 3.2
- Python versions 3.6 and 3.9

Maintained by `Basil Shubin <https://github.com/bashu>`_,  and some great
`contributors <https://github.com/bashu/wagtail-embedvideos/contributors>`_.

.. raw:: html

    <p align="center">
        <img src="https://raw.githubusercontent.com/bashu/wagtail-embedvideos/develop/screenshot.png">
    </p>

Installation
------------

First install the module, preferably in a virtual environment. It can be installed from PyPI:

.. code-block:: shell

    pip install wagtail-embedvideos

Requirements
~~~~~~~~~~~~

You must have *django-embed-video* installed and configured, see the
django-embed-video_ documentation for details and setup instructions.

Setup
-----

Make sure the project is configured for django-embed-video_.

Then add the following settings:

.. code-block:: python

    INSTALLED_APPS += (
        "wagtail_embed_videos",
    )

Then run ``./manage.py migrate`` to create the required database tables.

Usage
-----

In models, implement as a ``ForeignKey`` relation, same as ``wagtailimages``.

.. code-block:: python

    # models.py

    from wagtail.core.models import Page, PageBase

    from wagtail_embed_videos import get_embed_video_model_string
    from wagtail_embed_videos.edit_handlers import EmbedVideoChooserPanel

    class CustomPage(Page):
        video = models.ForeignKey(
            get_embed_video_model_string(),
            null=True, blank=True,
            on_delete=models.SET_NULL,
            related_name='+'
        )

        # ...

        content_panels = [
                EmbedVideoChooserPanel('video'),
        ]

In templates, load the ``embed_video_tags`` library in every template where you want to use it:

.. code-block:: html+django

    <!-- custom_page.html -->

    {% load embed_video_tags %}

    {% video self.video.url as my_video %}
        {% video my_video 'small' %}
    {% endvideo %}

Check django-embed-video_ documentation for more details.

Contributing
------------

If you like this module, forked it, or would like to improve it, please let us know!
Pull requests are welcome too. :-)

Credits
-------

`wagtail-embedvideos <https://github.com/bashu/wagtail-embedvideos/>`_ was originally started by `InfoPortugal, S.A. <https://github.com/infoportugal/>`_ who has now unfortunately abandoned the project.

License
-------

``wagtail-embedvideos`` is released under the BSD license.

.. _django-embed-video: https://github.com/jazzband/django-embed-video/
