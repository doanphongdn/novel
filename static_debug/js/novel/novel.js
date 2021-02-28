$(document).ready(function (e) {
    $(document).on('click', '.novel-action-bookmark', function () {
        const link = $(this);
        if (link.data("logged").toLowerCase() === 'false') {
            $('#modal-login').modal('toggle');
            return;
        }
        $.ajax({
            type: 'post',
            url: '/user/bookmark',
            data: {
                'status': link.data('status'),
                'novel_id': link.data('novel'),
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (data) {
                if (data.success === true) {
                    let status = data.bookmark_info.status
                    link.data("status", status);
                    link.children("p").text(data.bookmark_info.text);
                    link.children("button").text(data.bookmark_info.text);
                    link.children("i").class(status === "followed" ? "fa fa-check" : "fa fa-bookmark");
                }
            }
        });
    });
});