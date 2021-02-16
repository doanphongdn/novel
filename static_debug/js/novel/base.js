$(document).ready(function (e) {
    /* -------- START SEARCH ----------- */
    $('input.search').autocomplete({
        source: function (req, res) {
            $.ajax({
                type: "POST",
                url: "/search",
                dataType: 'json',
                data: {
                    q: req.term,
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function (json_data) {
                    res(json_data.data);
                }
            });
        },
        appendTo: "#search-area",
        minLength: 3,
        select: function (event, ui) {
            $(location).attr('href', ui.item.url);
        }
    }).data('ui-autocomplete')._renderItem = function (ul, v) {
        var html = '<li class="search-item ui-menu-item" tabindex="-1">';
        html += '<img src="' + v.thumbnail_image + '" alt="' + v.name + '">';
        html += '<h5 class="search-item-title">' + v.name + '</h5>';
        html += '</li>';
        return $(html).appendTo(ul);
    };
    /* -------- END SEARCH ----------- */

    $('.mobile-search-toggle').on('click', function (e) {
        $('.search-wrap').slideToggle('fast');
    });

    $("input.search").keydown(function (event) {
        if (event.keyCode == 13) {
            if ($("input.search").val().length == 0) {
                event.preventDefault();
                return false;
            }
        }
    });

    var lazy_param = {
        scrollDirection: 'vertical',
        effect: 'fadeIn',
        effectTime: 200,
        visibleOnly: true,
        onError: function (element) {
            element.attr("src", "/static/images/lazyload.gif")
        }
    };
    $('.lazyload').Lazy(lazy_param);

    $('#modal-login').on('show.bs.modal', function (e) {
        var button = $(e.relatedTarget);
        $(this).find("input:not([type=hidden])").each(function (index) {
            $(this).val("");
        });
        if (button.hasClass("btn-register")) {
            $(this).find('a.tab-register').tab('show');
        } else {
            $(this).find('a.tab-login').tab('show');
        }
    });
    $(".btn-reply-comment").on('click', function (t) {
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
        grecaptcha.execute(recapcha_site_key, {action: 'submit'}).then(function (token) {
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
                        grecaptcha.reset(recapcha_site_key);
                        if (form.hasClass("comment-reply-form")) {
                            form.parents('.comment-item').after(json_data.html);
                            form.remove();
                        } else {
                            $('.comment-list').prepend(json_data.html);
                        }
                    }
                }
            });
        });
    });
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
});