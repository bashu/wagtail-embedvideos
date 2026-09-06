/*
Wagtail's own per-chooser Telepath JS classes (e.g. wagtail.images' `ImageChooserFactory`,
in image-chooser-telepath.js) aren't exposed as public globals - they, and the base
`ChooserFactory`/`Chooser` classes they extend, are bundled directly into Wagtail's own
webpack chunk (see wagtailadmin/js/chooser-widget-telepath.js). So, same as
embed-video-chooser.js and embed-video-chooser-modal.js already do for the non-Telepath
widget and modal-onload paths, this vendors a minimal copy of Wagtail's `ChooserFactory`
(client/src/components/ChooserWidget/index.js) rather than trying to subclass it directly.

Telepath is what lets StreamField build/update widget state entirely client-side - adding a
new block, duplicating one, undo/redo, and revision-preview diffing all go through this
rather than a full page round-trip. `EmbedVideoChooserBlock` (a StreamField `ChooserBlock`)
relies on it for exactly that. Without this file (and its Python counterpart,
`EmbedVideoChooserAdapter` in widgets.py), StreamField would silently fall back to Wagtail's
own generic `wagtail.admin.widgets.Chooser` Telepath widget, which knows nothing about our
extra `preview` (thumbnail) state - so choosing/changing a video inside a StreamField block
would update the title/link but never create or update the thumbnail preview.
*/
class EmbedVideoChooserFactory {
    widgetClass = EmbedVideoChooser;

    constructor(html, idPattern, opts = {}) {
        this.html = html;
        this.idPattern = idPattern;
        this.opts = opts;
    }

    render(placeholder, name, id, initialState) {
        const html = this.html.replace(/__NAME__/g, name).replace(/__ID__/g, id);
        placeholder.outerHTML = html;
        const chooser = new this.widgetClass(id, this.opts);
        chooser.setState(initialState);
        return chooser;
    }

    /** Retrieve the widget object corresponding to the given HTML ID. */
    getById(id) {
        return document.getElementById(`${id}-chooser`).widget;
    }

    /** Retrieve the widget object corresponding to the given HTML name. */
    getByName(name, container) {
        const input = container.querySelector(`input[name="${name}"]`);
        return this.getById(input.id);
    }
}
window.telepath.register(
    'wagtail_embed_videos.widgets.AdminEmbedVideoChooser',
    EmbedVideoChooserFactory,
);
