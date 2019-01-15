function createEmbedVideoChooser(id) {
    var chooserElement = $('#' + id + '-chooser');
    var previewEmbedVideo = chooserElement.find('.preview-image img');
    var input = $('#' + id);
    var editLink = chooserElement.find('.edit-link');

    $('.action-choose', chooserElement).click(function() {
        ModalWorkflow({
            'url': window.chooserUrls.embedVideoChooser,
            'onload': {
                'chooser': function(modal, jsonData) {
                    var searchUrl = $('form.embed-video-search', modal.body).attr('action');

                    function ajaxifyLinks (context) {
                        $('.listing a', context).click(function() {
                            modal.loadUrl(this.href);
                            return false;
                        });

                        $('.pagination a', context).click(function() {
                            var page = this.getAttribute("data-page");
                            setPage(page);
                            return false;
                        });
                    }

                    function search() {
                        $.ajax({
                            url: searchUrl,
                            data: {q: $('#id_q').val()},
                            success: function(data, status) {
                                $('#embed-video-results').html(data);
                                ajaxifyLinks($('#embed-video-results'));
                            }
                        });
                        return false;
                    }

                    function setPage(page) {
                        if($('#id_q').val().length){
                            dataObj = {q: $('#id_q').val(), p: page};
                        }else{
                            dataObj = {p: page};
                        }

                        $.ajax({
                            url: searchUrl,
                            data: dataObj,
                            success: function(data, status) {
                                $('#embed-video-results').html(data);
                                ajaxifyLinks($('#embed-video-results'));
                            }
                        });
                        return false;
                    }

                    ajaxifyLinks(modal.body);

                    $('form.embed-video-search', modal.body).submit(search);

                    $('#id_q').on('input', function() {
                        clearTimeout($.data(this, 'timer'));
                        var wait = setTimeout(search, 200);
                        $(this).data('timer', wait);
                    });
                    $('a.suggested-tag').click(function() {
                        $('#id_q').val($(this).text());
                        search();
                        return false;
                    });

                    //{% url 'wagtailadmin_tag_autocomplete' as autocomplete_url %}

                    /* Add tag entry interface (with autocompletion) to the tag field of the embed video upload form */
                    $('#id_tags', modal.body).tagit({
                        autocomplete: {source: jsonData.autocomplete_url}
                    });
                },
                'embed_video_chosen': function(modal, jsonData) {
                    modal.respond('embedVideoChosen', jsonData);
                    modal.close();
                },
                'select_format': function(modal) {
                    $('form', modal.body).submit(function() {
                        var formdata = new FormData(this);

                        $.post(this.action, $(this).serialize(), function(response){
                            modal.loadResponseText(response);
                        }, 'text');

                        return false;
                    });
                },
            },
            'responses': {
                'embedVideoChosen': function(embedVideoData) {
                    input.val(embedVideoData.id);
                    previewEmbedVideo.attr({
                        'src': embedVideoData.preview.url,
                        'alt': embedVideoData.title
                    });
                    chooserElement.removeClass('blank');
                    editLink.attr('href', embedVideoData.edit_link);
                }
            }
        });
    });

    $('.action-clear', chooserElement).click(function() {
        input.val('');
        chooserElement.addClass('blank');
    });
}
