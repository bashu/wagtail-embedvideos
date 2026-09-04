/*
Wagtail 4.x exposes its chooser-modal machinery as `window.ChooserModalOnloadHandlerFactory`
via wagtailadmin/js/chooser-modal.js specifically so third-party choosers can extend it from
plain, non-webpack JS like this file (see widgets.py's `media` property for the load order
this depends on). This mirrors Wagtail's own wagtail.images equivalent, image-chooser-modal.js.
*/
class EmbedVideoChooserModalOnloadHandlerFactory extends window.ChooserModalOnloadHandlerFactory {
    ajaxifyLinks(modal, context) {
        super.ajaxifyLinks(modal, context);

        // Lives inside the results listing's "no items" message, which is
        // replaced on every search/pagination refresh, so it needs rebinding
        // each time `ajaxifyLinks` runs.
        $('a.upload-one-now').on('click', (event) => {
            // Carry the current collection filter over to the upload form's
            // own collection field.
            const collectionId = $('#id_collection_id').val();
            if (collectionId) {
                $('#id_embed_video-chooser-upload-collection').val(collectionId);
            }
            event.preventDefault();
        });
    }

    onLoadChooseStep(modal) {
        super.onLoadChooseStep(modal);

        // Lives inside the filter form, which is rendered once and never
        // replaced by a search/pagination refresh, so this only needs
        // binding once, here, rather than on every `ajaxifyLinks` call.
        $('a.suggested-tag').on('click', (event) => {
            $('#id_q').val('');
            this.searchController.search({
                tag: $(event.currentTarget).text(),
                collection_id: $('#id_collection_id').val(),
            });
            return false;
        });
    }
}

window.EMBEDVIDEO_CHOOSER_MODAL_ONLOAD_HANDLERS = new EmbedVideoChooserModalOnloadHandlerFactory({
    creationFormTabSelector: '#tab-upload',
}).getOnLoadHandlers();
