function(modal) {
    modal.respond('embedVideoChosen', {{ embed_video_json|safe }});
    modal.close();
}
