function createEmbedVideoChooser(id) {
    var chooserElement = $('#' + id + '-chooser');
    var previewEmbedVideo = chooserElement.find('.preview-embedvideo img');
    var input = $('#' + id);
    var editLink = chooserElement.find('.edit-link');

    $('.action-choose', chooserElement).on('click', function() {
        ModalWorkflow({
            url: chooserElement.data('chooserUrl'),
            onload: EMBEDVIDEO_CHOOSER_MODAL_ONLOAD_HANDLERS,
            responses: {
                embedVideoChosen: function(embedVideoData) {
                    input.val(embedVideoData.id);
                    previewEmbedVideo.attr({
                        src: embedVideoData.preview.url,
                        width: embedVideoData.preview.width,
                        height: embedVideoData.preview.height,
                        alt: embedVideoData.title,
                        title: embedVideoData.title
                    });
                    chooserElement.removeClass('blank');
                    editLink.attr('href', embedVideoData.edit_link);
                }
            }
        });
    });

    $('.action-clear', chooserElement).on('click', function() {
        input.val('');
        chooserElement.addClass('blank');
    });
}
