$(document).ready(function (e) {
    $(document).on('click', '.btn-reply-comment', function (t) {
        let parent_obj = $(this).parents(".comment-content-reply");
        let reply_id = $(this).data('comment-id');
        let parent_id = $(this).data('parent-id');
        let novel_id = $("form.comment-form").find("#id_novel_id").val();
        let chapter_id = $("form.comment-form").find("#id_chapter_id").val();
        $.ajax({
            type: "POST",
            url: "/comment/form",
            dataType: 'json',
            data: {
                parent_id: parent_id,
                reply_id: reply_id,
                novel_id: novel_id,
                chapter_id: chapter_id,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (json_data) {
                for (instance in CKEDITOR.instances) {
                    if (instance !== 'cke_novel_id') {
                        CKEDITOR.instances[instance].destroy();
                    }
                }
                $(".comment-list form.comment-reply-form").remove();
                $(json_data.html).appendTo(parent_obj);
                $.each($("form.comment-reply-form textarea"), function (i, v) {
                    CKEDITOR.replace(v.id, JSON.parse(v.getAttribute("data-config")));
                })
            }
        });
    });
    $(document).on('submit', '.comment-form, .comment-reply-form', function (e) {
        let form = $(this);
        e.preventDefault();
        for (instance in CKEDITOR.instances) {
            CKEDITOR.instances[instance].updateElement();
        }
        var form_data = $(this).serializeArray();
        grecaptcha.execute(recaptcha_site_key, {action: 'submit'}).then(function (token) {
            form_data.push({name: 'g-recaptcha-response', value: $("*[name='g-recaptcha-response']").val()});
            $.ajax({
                type: "POST",
                url: "/comment",
                dataType: 'json',
                data: form_data,
                success: function (json_data) {
                    if (json_data.success) {
                        for (instance in CKEDITOR.instances) {
                            CKEDITOR.instances[instance].updateElement();
                        }
                        CKEDITOR.instances[instance].setData('');
                        if (form.hasClass("comment-reply-form")) {
                            form.parents('.comment-item').after(json_data.html);
                            form.remove();
                        } else {
                            $('.comment-list').prepend(json_data.html);
                        }
                        $("#comment-error").html("");
                    } else {
                        console.log(json_data.message);
                        $("#comment-error").html(json_data.message);
                    }
                    grecaptcha.reset(recaptcha_site_key);
                }
            });
        });
    });
});
