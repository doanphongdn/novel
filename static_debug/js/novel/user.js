$(document).ready(function (e) {
    $(document).on('submit', '#register-form', function (e) {
        e.preventDefault();
        var form = $(this);
        $.ajax({
            type: 'post',
            url: '/user/signup',
            data: form.serializeArray(),
            success: function (data) {
                if (data.success == false) {
                    $('.message.register').html("");
                    $.each(data.errors, function (i, e) {
                        $('.message.register').append(e + "</br>");
                    })
                } else {
                    location.reload();
                }
            }
        });
    });
    $(document).on('submit', '#login-form', function (e) {
        e.preventDefault();
        var form = $(this);
        $.ajax({
            type: 'post',
            url: '/user/signin',
            data: form.serializeArray(),
            success: function (data) {
                $('.message.login').html("");
                if (data.success === true) {
                    $(location).attr('href', data.redirect_to);
                } else {
                    $.each(data.errors, function (i, e) {
                        $('.message.login').append(e + "</br>");
                    })
                }
            }
        });
    });
    $(document).on('click', '.novel-wrap > .btn-remove ', function () {
        novel_id = $(this).data("id");
        action = $(this).data("action");
        $.ajax({
            type: 'post',
            url: '/user/novel-remove',
            data: {
                'action': action,
                'novel_id': novel_id,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (data) {
                if (data.success === true) {
                    location.reload();
                }
            }
        });
    });


});