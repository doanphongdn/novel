$(document).ready(function (e) {
    $('input.search').autocomplete({
        source: function (req, res) {
            $.ajax({
                type: "POST",
                url: "/novel/search",
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
    $('.mobile-search-toggle').on('click', function (e) {
        $('.search-wrap').slideToggle('fast');
    });

    var fontSizeSlider = document.getElementById('fontSizeSlider');
    var fontWeightSlider = document.getElementById('fontWeightSlider');
    var lineHeightSlider = document.getElementById('lineHeightSlider');
    if ($('#fontSizeSlider').length != 0) {
        noUiSlider.create(fontSizeSlider, {
            start: 20,
            step: 5,
            connect: [true, false],
            range: {
                'min': 15,
                'max': 40
            }
        }).on('update', function (values, handle) {
            $(".chapter-detail p").css("font-size", values[handle] + "px");
        });
    }
    ;
    if ($('#fontWeightSlider').length != 0) {
        noUiSlider.create(fontWeightSlider, {
            start: 200,
            step: 200,
            connect: [true, false],
            range: {
                'min': 200,
                'max': 800
            }
        }).on('update', function (values, handle) {
            $(".chapter-detail p").css("font-weight", values[handle]);
        });
    }
    ;
    if ($('#lineHeightSlider').length != 0) {
        noUiSlider.create(lineHeightSlider, {
            start: 200,
            step: 50,
            connect: [true, false],
            range: {
                'min': 150,
                'max': 400
            }
        }).on('update', function (values, handle) {
            $(".chapter-detail p").css("line-height", values[handle] + "%");
        });
    }
    ;
    var colorButton = $(".colors li");

    colorButton.on("click", function () {
        // Remove class from currently active button
        $(".colors > li").removeClass("active-color");

        // Add class active to clicked button
        $(this).addClass("active-color");

        // Get background color of clicked
        var newColor = $(this).data("color");
        var newTextColor = $(this).data("text-color");

        // Change background of everything with class .bg-color
        $("body").css("background-color", newColor);
        if (newTextColor == undefined) {
            newTextColor = "#243239";
            $(".chapter-actions button").removeClass('btn-secondary').addClass('btn-default');
        } else {
            $(".chapter-actions button").removeClass('btn-default').addClass('btn-secondary');
        }
        // Change color of everything with class .text-color
        $(".chapter-title h3").css("color", newTextColor);
        $(".chapter-title h5").css("color", newTextColor);
        $(".chapter-detail p").css("color", newTextColor);
        $(".float-button li i").css("color", newTextColor);
        $(".widget-breadcrumb a").css("color", newTextColor);
    });
});