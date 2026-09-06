Changes
-------

6.3.0 (2026-09-06)
~~~~~~~~~~~~~~~~~~

* Wagtail version 6.3 supported. Dropped support for Wagtail < 6.3.
* Python 3.13 supported, alongside 3.10 to 3.12.
* Django version 5.1 supported; dropped 5.0.

6.2.0 (2026-09-06)
~~~~~~~~~~~~~~~~~~

* Wagtail version 6.2 supported. Dropped support for Wagtail < 6.2.

6.1.0 (2026-09-06)
~~~~~~~~~~~~~~~~~~

* Wagtail version 6.1 supported. Dropped support for Wagtail < 6.1.

6.0.0 (2026-09-06)
~~~~~~~~~~~~~~~~~~

* Wagtail version 6.0 supported. Dropped support for Wagtail < 6.0.
* Python 3.12 supported, alongside 3.10 and 3.11.
* Django version 5.0 only; dropped 4.2.

5.2.0 (2026-09-04)
~~~~~~~~~~~~~~~~~~

* Wagtail version 5.2 supported. Dropped support for Wagtail < 5.2.
* Django version 5.0 supported, alongside 4.2.

5.1.0 (2026-09-04)
~~~~~~~~~~~~~~~~~~

* Wagtail version 5.1 supported. Dropped support for Wagtail < 5.1.
* Registered ``EmbedVideoDisplay`` (``wagtail_embed_videos/components.py``)
  for any ``ForeignKey`` to the embed video model, via Wagtail 5.1's new
  ``register_display_class`` API. Embed video fields shown on a model's
  generic inspect view now render as an actual embedded iframe instead
  of the video's plain title text.

5.0.1 (2026-09-04)
~~~~~~~~~~~~~~~~~~

* Fixed the embed video edit and add pages, which were completely broken
  under Wagtail 5.0: both included
  ``wagtailadmin/pages/_editor_css.html``, a template Wagtail 5.0 removed
  (``insert_editor_css`` is now emitted unconditionally by
  ``admin_base.html`` itself, making the include redundant even before
  it broke).
  Also fixed a missing closing ``</div>`` on the edit page left over from
  an earlier restructure.
* Made the video preview on the edit page responsive (scales with the
  viewport instead of a fixed 480x360 box), via a CSS
  ``aspect-ratio``-based wrapper.
* ``EmbedVideoChooserBlock.render_basic()`` now passes its ``context``
  through to ``VideoNode.embed()``, so StreamField-embedded videos get
  a correctly secure/insecure embed URL based on the current request
  instead of always defaulting to one or the other.
* The homepage summary count now reflects only videos the user has
  permission for, rather than the total count across all videos.
* Added ``djlint`` for template linting/formatting.

5.0.0 (2026-09-04)
~~~~~~~~~~~~~~~~~~

* Wagtail version 5.0 supported. Dropped support for Wagtail < 5.0.
* Python 3.10 and 3.11 supported; dropped 3.8/3.9. Django 4.2 only;
  dropped 3.2/4.0/4.1.

4.2.0 (2026-09-04)
~~~~~~~~~~~~~~~~~~

* Wagtail version 4.2 supported. Dropped support for Wagtail < 4.2.
* Widget's JS hookup switched from an overridden ``render_js_init()`` to
  Wagtail 4.2's declarative ``js_constructor`` attribute on
  ``BaseChooser``.
* Added multiple-choice support to the chooser (``ChosenMultipleViewMixin``,
  ``chosen_multiple_view_class``), and preserved URL parameters on the
  chosen link, matching Wagtail 4.2's ``ChooserViewSet`` conventions.
* Fixed a URL namespace typo in the bulk-delete confirmation template
  (``wagtail_embed_video:edit`` -> ``wagtail_embed_videos:edit``).
* Guarded the embed video listing search against an empty query string.
* Fixed the chooser widget's JS for Wagtail 4.2's ``Chooser.openChooserModal()``
  rewrite, which dropped the ``modalOnloadHandlers`` widget property in favour
  of a ``chooserModalClass`` (a ``ChooserModal`` subclass carrying its own
  ``onloadHandlers``); left as-is, the widget would have silently fallen back
  to the default (non-customised) chooser-modal behaviour, with no error.
  Since ``ChooserModal`` isn't exposed as a public global (only Wagtail's own
  webpack-bundled entrypoints can subclass it directly), ``EmbedVideoChooser``
  now overrides ``openChooserModal()`` to construct the inherited default
  modal class and swap in our own onload handlers on the instance instead.

4.1.0 (2026-09-04)
~~~~~~~~~~~~~~~~~~

* Wagtail version 4.1 supported. Dropped support for Wagtail < 4.1.
* Switched ``get_usage()`` to Wagtail 4.1's ``ReferenceIndex`` API
  (``wagtail.models.ReferenceIndex.get_references_to(self).group_by_source_object()``),
  replacing the old reflection-based ``get_object_usage()``. Existing
  installations must run ``./manage.py rebuild_references_index`` once
  after upgrading, to backfill usage data for content saved before the
  upgrade.
* The embed video "usage" view now checks "change" permission on the
  specific instance, and resolves proper edit URLs/labels for
  referencing objects via ``AdminURLFinder``; the usage template shows
  which field/content path each reference comes from.
* Added a usage count link to the embed video edit page, and removed
  the ``usage_count_enabled`` feature-flag guard around usage counts
  on the delete/bulk-delete confirmation templates (usage counting is
  now always available via ``ReferenceIndex``).
* Fixed ``get_valid_next_url_from_request`` import
  (``wagtail.admin.views.pages.utils`` moved to ``wagtail.admin.utils``
  in Wagtail 4.1).

4.0.0 (2026-09-04)
~~~~~~~~~~~~~~~~~~

* Wagtail version 4.x supported. Dropped support for Wagtail < 4.0.
* Rewrote the embed video chooser (widget, views and JS) on Wagtail 4.x's
  generic chooser framework (``wagtail.admin.views.generic.chooser``,
  ``wagtail.admin.viewsets.chooser.ChooserViewSet``,
  ``wagtail.admin.widgets.BaseChooser``), replacing the old
  ``AdminChooser``/``ModalWorkflow``-based implementation.
* Dropped the vendored ``tabs.js``: Wagtail 4.x exposes its own chooser-modal
  JS (``window.Chooser``, ``window.ChooserModalOnloadHandlerFactory``) as
  public globals for exactly this purpose, so it's no longer needed.
* Dropped support for Python 3.7 (no longer obtainable via ``uv``/
  ``python-build-standalone``; EOL since June 2023). Python versions
  3.8 to 3.10 supported.
* Excluded the ``tests`` package from the built wheel/sdist.

3.0.0 (2026-09-04)
~~~~~~~~~~~~~~~~~~

* Wagtail version 3.x supported. Dropped support for Wagtail < 3.0.
* Django versions 3.2 and 4.0 supported. Dropped support for Django < 3.2.
* Python versions 3.8 to 3.10 supported.
* Vendored Wagtail's own ``tabs.js`` into the embed video chooser modal, since
  Wagtail 3.x no longer exposes it as a public global, restoring full keyboard
  accessibility for the chooser's tabbed UI.
* Migrated packaging from ``setup.py``/``setup.cfg`` to ``pyproject.toml``.
* Switched CI from Travis to GitHub Actions.
* Fixed broken imports.

0.5.12 (2022-04-20)
~~~~~~~~~~~~~~~~~~~

* Fixed broken imports.

0.5.11 (2021-12-13)
~~~~~~~~~~~~~~~~~~~

* Added ru translation.

0.5.10 (2021-12-06)
~~~~~~~~~~~~~~~~~~~

* Fixed stupid typo.

0.5.9 (2021-12-06)
~~~~~~~~~~~~~~~~~~

* Wagtail version >= 2.15 supported.

0.5.8 (2021-11-12)
~~~~~~~~~~~~~~~~~~

* Wagtail version >= 2.14 supported.

0.5.7 (2021-11-11)
~~~~~~~~~~~~~~~~~~

* Wagtail version >= 2.13 supported.

0.5.6 (2021-11-10)
~~~~~~~~~~~~~~~~~~

* Wagtail version >= 2.12 supported.

0.5.5 (2021-11-09)
~~~~~~~~~~~~~~~~~~

* Wagtail version >= 2.11 supported.

0.5.4 (2021-11-08)
~~~~~~~~~~~~~~~~~~

* Wagtail version >= 2.10 supported.

0.5.3 (2021-11-07)
~~~~~~~~~~~~~~~~~~

* Replacing broken 0.5.2 release.

0.5.2 (2021-11-06)
~~~~~~~~~~~~~~~~~~

* Wagtail version >= 2.9 supported.

0.5.1 (2021-11-05)
~~~~~~~~~~~~~~~~~~

* Wagtail version >= 2.8 supported.

0.5.0 (2021-11-04)
~~~~~~~~~~~~~~~~~~

* Wagtail version >= 2.4 supported.
* Dropped support for Python < 3.x.

0.4.1 (2018-08-22)
~~~~~~~~~~~~~~~~~~

* Wagtail version >= 2.x supported.
* Django version >= 2.x supported.
* Dropped support for Wagtail < 2.x.

0.3.0 (2017-04-24)
~~~~~~~~~~~~~~~~~~

* Changed the structure of "AbstractEmbedVideo", because "TagSearchable" is not used anymore.

0.2.5 (2017-02-09)
~~~~~~~~~~~~~~~~~~

* This is the last version compatible with Wagtail <= 1.6, because TagSearchable was deprecated and then removed.
