/*
Wagtail's own tab-switching behaviour (wagtailadmin/js/vendor.js) is bundled as a
webpack module that isn't exposed on `window`, so it can't be called from plain,
non-webpack static files like this one. wagtail_embed_videos/js/vendor/tabs.js is a
vendored, behavior-identical copy of Wagtail's own client/src/includes/tabs.js for
that reason. This just scopes (re)initialization to the modal's own tab markup,
instead of the whole document, so it can be re-run whenever the modal's tab markup
is (re)loaded via AJAX without re-binding tabs elsewhere on the underlying page.
*/
function initEmbedVideoChooserTabs(modal) {
    var tabs = modal.body.get(0).querySelectorAll('[data-tabs]');
    window.WagtailEmbedVideosTabs.initTabs(tabs);
}

function ajaxifyEmbedVideoUploadForm(modal) {
    $('form.embed_video-upload', modal.body).on('submit', function() {
        var formdata = new FormData(this);

        if (!$('#id_embed_video-chooser-upload-title', modal.body).val()) {
            var li = $('#id_embed_video-chooser-upload-title', modal.body).closest('li');
            if (!li.hasClass('error')) {
                li.addClass('error');
                $('#id_embed_video-chooser-upload-title', modal.body)
                    .closest('.field-content')
                    .append(
                        '<p class="error-message"><span>This field is required.</span></p>',
                    );
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
                    var message = jsonData.error_message + '<br />' + errorThrown + ' - ' + response.status;
                    $('#tab-upload', modal.body).append(
                        '<div class="help-block help-critical">' +
                            '<strong>' + jsonData.error_label + ': </strong>' + message + '</div>');
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
            };
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
                tag: $(this).text(),
                collection_id: $('#collection_chooser_collection_id').val()
            });
            return false;
        });

        // Reinitialize tabs to hook up tab event listeners in the modal
        initEmbedVideoChooserTabs(modal);
    },
    'embed_video_chosen': function(modal, jsonData) {
        modal.respond('embedVideoChosen', jsonData.result);
        modal.close();
    },
    'reshow_upload_form': function(modal, jsonData) {
        $('#tab-upload', modal.body).replaceWith(jsonData.htmlFragment);
        initEmbedVideoChooserTabs(modal);
        ajaxifyEmbedVideoUploadForm(modal);
    },
};
