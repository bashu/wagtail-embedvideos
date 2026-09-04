/*
Wagtail 4.x exposes its base chooser widget JS class as `window.Chooser` via
wagtailadmin/js/chooser-widget.js, specifically so third-party choosers can extend
it from plain, non-webpack JS like this file (see widgets.py's `media` property for
the load order this depends on). This mirrors Wagtail's own wagtail.images equivalent,
image-chooser.js.
*/
class EmbedVideoChooser extends window.Chooser {
    modalOnloadHandlers = window.EMBEDVIDEO_CHOOSER_MODAL_ONLOAD_HANDLERS;

    initHTMLElements(id) {
        super.initHTMLElements(id);
        this.previewImage = this.chooserElement.querySelector('[data-chooser-image]');
    }

    getStateFromHTML() {
        /*
        Construct initial state of the chooser from the rendered (static) HTML.
        State is either null (= no embed video chosen) or a dict of id, edit_url,
        title and preview (= a dict of url, width, height).
        */
        const state = super.getStateFromHTML();
        if (state) {
            state.preview = {
                url: this.previewImage.getAttribute('src'),
                width: this.previewImage.getAttribute('width'),
                height: this.previewImage.getAttribute('height'),
            };
        }
        return state;
    }

    renderState(newState) {
        super.renderState(newState);
        this.previewImage.setAttribute('src', newState.preview.url);
        this.previewImage.setAttribute('width', newState.preview.width);
        this.previewImage.setAttribute('height', newState.preview.height);
    }
}
window.EmbedVideoChooser = EmbedVideoChooser;

function createEmbedVideoChooser(id) {
    /* legacy factory kept for third-party code still calling it directly;
    widgets.py's own render_js_init now emits `new EmbedVideoChooser(id)`. */
    return new EmbedVideoChooser(id);
}
window.createEmbedVideoChooser = createEmbedVideoChooser;
