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
});