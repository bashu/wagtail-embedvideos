function ajaxifyEmbedVideoUploadForm(modal) {
    $('form.embed_video-upload', modal.body).on('submit', function() {
        var formdata = new FormData(this);

        if ($('#id_embed_video-chooser-upload-title', modal.body).val() == '') {
            var li = $('#id_embed_video-chooser-upload-title', modal.body).closest('li');
            if (!li.hasClass('error')) {
                li.addClass('error');
                $('#id_embed_video-chooser-upload-title', modal.body).closest('.field-content').append('<p class="error-message"><span>This field is required.</span></p>')
            }
            setTimeout(cancelSpinner, 500);
        } else {
            $.ajax({
                url: this.action,
                data: formdata,
                processData: false,
                contentType: false,
                type: 'POST',
                dataType: 'text',
                success: modal.loadResponseText,
                error: function(response, textStatus, errorThrown) {
                    var message = jsonData['error_message'] + '<br />' + errorThrown + ' - ' + response.status;
                    $('#upload').append(
                        '<div class="help-block help-critical">' +
                            '<strong>' + jsonData['error_label'] + ': </strong>' + message + '</div>');
                }
            });
        }

        return false;
    });
}

EMBEDVIDEO_CHOOSER_MODAL_ONLOAD_HANDLERS = {
    'chooser': function(modal, jsonData) {
        var searchForm = $('form.embed_video-search', modal.body);
        var searchUrl = searchForm.attr('action');

        /* currentTag stores the tag currently being filtered on, so that we can
        preserve this when paginating */
        var currentTag;

        function ajaxifyLinks (context) {
            $('.listing a', context).on('click', function() {
                modal.loadUrl(this.href);
                return false;
            });

            $('.pagination a', context).on('click', function() {
                fetchResults(this.href);
                return false;
            });
        }
        var request;

        function fetchResults(url, requestData) {
            var opts = {
                url: url,
                success: function(data, status) {
                    request = null;
                    $('#embed_video-results').html(data);
                    ajaxifyLinks($('#embed_video-results'));
                },
                error: function() {
                    request = null;
                }
            }
            if (requestData) {
                opts.data = requestData;
            }
            request = $.ajax(opts);
        }

       function search() {
            fetchResults(searchUrl, searchForm.serialize());
            return false;
        }

        ajaxifyLinks(modal.body);
        ajaxifyEmbedVideoUploadForm(modal);

        $('form.embed_video-search', modal.body).on('submit', search);

        $('#id_q').on('input', function() {
            if (request) {
                request.abort();
            }
            clearTimeout($.data(this, 'timer'));
            var wait = setTimeout(search, 200);
            $(this).data('timer', wait);
        });
        $('#collection_chooser_collection_id').on('change', search);
        $('a.suggested-tag').on('click', function() {
            $('#id_q').val('');
            fetchResults(searchUrl, {
                'tag': $(this).text(),
                collection_id: $('#collection_chooser_collection_id').val()
            });
            return false;
        });
    },
    'embed_video_chosen': function(modal, jsonData) {
        modal.respond('embedVideoChosen', jsonData['result']);
        modal.close();
    },
    'reshow_upload_form': function(modal, jsonData) {
        $('#upload', modal.body).replaceWith(jsonData.htmlFragment);
        ajaxifyEmbedVideoUploadForm(modal);
    },
};
