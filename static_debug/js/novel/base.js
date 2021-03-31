$(document).ready(function (e) {
    // history.scrollRestoration = "manual";
    // $(window).scrollTop(0);
    $("#ads-scroll-left, #ads-scroll-right").css({"opacity": "0"});
    let baseTopAdsHeight = 0;
    let limit_top = 120;
    let stateCheck = setInterval(() => {
        if (document.readyState === 'complete') {
            $("#ads-scroll-left, #ads-scroll-right").css({"opacity": "1"});
            if ($("#base-top-ads").length) {
                baseTopAdsHeight = $("#base-top-ads")[0].offsetHeight;
                $("#ads-scroll-left, #ads-scroll-right").css({"top": (baseTopAdsHeight + limit_top) + "px"});
            }
            clearInterval(stateCheck);
        }
    }, 100);

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
            $.ajax({
                type: "POST",
                url: "/update_point",
                dataType: 'json',
                data: {
                    q: ui.item,
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function (json_data) {
                    console.log(json_data.data);
                }
            });
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

    $("img.lazyload").lazyload();
    //
    // var lazy_param = {
    //     scrollDirection: 'vertical',
    //     effect: 'fadeIn',
    //     delay: 5000,
    //     effectTime: 100,
    //     threshold: 1000,
    //     visibleOnly: true,
    //     onError: function (element) {
    //         element.attr("src", "/static/images/lazyload.gif")
    //     }
    // };
    // $('.lazyload').Lazy(lazy_param);

    $('#mobile-menu-action').on('change', function () {
        if (this.checked) {
            $("body").css({"overflow": "hidden"});
            $("#mobile-menu").css({
                "position": "fixed",
                "top": "20px",
            });
        } else {
            $("#mobile-menu").css({
                "position": "",
                "top": "",
            });
            $("body").css({"overflow": ""});
        }
    });

    $(document).scroll(function () {
        var scrollTop = $(document).scrollTop();
        var menuTop = $('.navbar-top-menu .scrollable');
        var menuTopHeight = 0;
        var menuNavbarHeight = 0;
        var footerHeight = 0;
        if (menuTop !== undefined) {
            menuTopHeight = menuTop[0].offsetHeight;
            var navbar_base = $('.navbar-base')[0];
            var menuTopWidth = menuTop[0].offsetWidth;
            if (scrollTop - (navbar_base.offsetTop + navbar_base.offsetHeight) > 0) {
                menuTop.css({
                    'width': menuTopWidth + "px",
                    'position': "fixed",
                    'top': "0",
                    'z-index': "1000",
                });
            } else {
                menuTop.css('position', "relative");
                menuTop.css('width', "100%");
            }
        }
        var menu_action = $('.chapter-actions');
        if (menu_action.length) {
            menu_action_item = menu_action[0];
            menuNavbarHeight = menu_action_item.offsetHeight;
            var contentTop = $('.chapter-content').offset().top;
            var menuWidth = menu_action_item.offsetWidth;
            if (scrollTop - contentTop + menuTopHeight > 0) {
                menu_action.css({
                    'width': menuWidth + "px",
                    'position': "fixed",
                    'top': menuTopHeight + "px",
                    'z-index': "1000",
                    'box-shadow': "0 1px 10px rgba(50,50,93,.1),0 1px 5px rgba(0,0,0,.07)!important",
                });
            } else {
                menu_action.css({
                    'top': 0,
                    'position': "absolute",
                    'width': "100%"
                });
            }
        }

        if ($(".footer").length)
            footerHeight = $(".footer")[0].offsetHeight;

        $("#ads-scroll-left").scroll_ads_horizotal(scrollTop, baseTopAdsHeight, footerHeight);
        $("#ads-scroll-right").scroll_ads_horizotal(scrollTop, baseTopAdsHeight, footerHeight);
    });

    // Function
    $.fn.scroll_ads_horizotal = function (scrollTop, baseTopAdsHeight, footerHeight) {
        if (!this.length)
            return;

        top_pos = $(document).height() - scrollTop - footerHeight - this[0].offsetHeight - 20;
        if (top_pos > limit_top) {
            top_pos = limit_top;
            if (scrollTop < baseTopAdsHeight) {
                top_pos = limit_top + baseTopAdsHeight - scrollTop;
            }
        }
        this.css("top", top_pos + "px");
    };
    $(document).on('click', '.novel-action-bookmark', function (e) {
        e.preventDefault();
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
                    link.children("i").attr('class', status === "followed" ? "fa fa-check" : "fa fa-bookmark");
                }
            }
        });
    });

    $(document).on('click', '.notify-message', function (e) {
        e.preventDefault();
        let notify_id = $(this).data("id");
        $.ajax({
            type: 'post',
            url: '/user/read_notify',
            data: {
                'notify_id': notify_id,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (data) {
                // if (data.success === true && data.redirect_url) {
                //     window.location.href = data.redirect_url;
                // }
            }
        });
    })
});