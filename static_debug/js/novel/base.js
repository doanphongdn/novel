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

    var lazy_param = {
        scrollDirection: 'vertical',
        effect: 'fadeIn',
        effectTime: 200,
        threshold: 1000,
        visibleOnly: true,
        onError: function (element) {
            element.attr("src", "/static/images/lazyload.gif")
        }
    };
    $('.lazyload').Lazy(lazy_param);

    $('#navbar-danger').on('hidden.bs.collapse', function () {
        $("body").css({"position": ""});
        $("#backdrop").hide();
    });
    $('#navbar-danger').on('show.bs.collapse', function () {
        $("body").css({"position": "fixed"});
        $("#backdrop").show();
    });

    $(document).on('resize', function (e){

        alert(this.offset().width());
    });
});