$(document).ready(function (e) {

    function setBackgroundColor(newBgColor) {
        // Change background of everything with class .bg-color
        $("body").css("background-color", newBgColor);
    }

    function setElementsColor(newTextColor) {
        $(".chapter-title h3").css("color", newTextColor);
        $(".chapter-title h5").css("color", newTextColor);
        $(".chapter-detail p").css("color", newTextColor);
        $(".float-button li i").css("color", newTextColor);
        $(".widget-breadcrumb a").css("color", newTextColor);
    }

    function setChapterFontSize(fontSize) {
        $(".chapter-detail p").css("font-size", fontSize + "px");
    }

    function setChapterFontWeight(fontWeight) {
        $(".chapter-detail p").css("font-weight", fontWeight);
    }

    function setChapterLineHeight(lineHeight) {
        $(".chapter-detail p").css("line-height", lineHeight + "%");
    }

    /* -------- START SEARCH ----------- */
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
    /* -------- END SEARCH ----------- */

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
        }).on('change.one', function (values, handle) {
            let fontSize = values[handle];
            $(".chapter-detail p").css("font-size", fontSize + "px");
            Cookies.set('fontSizeSlider', fontSize);
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
        }).on('change.one', function (values, handle) {
            let fontWeight = values[handle];
            $(".chapter-detail p").css("font-weight", fontWeight);
            Cookies.set('fontWeightSlider', fontWeight);
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
        }).on('change.one', function (values, handle) {
            let lineHeight = values[handle];
            $(".chapter-detail p").css("line-height", lineHeight + "%");
            Cookies.set('lineHeightSlider', lineHeight);
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
        var newBgColor = $(this).data("color");
        var newTextColor = $(this).data("text-color");

        // Verify the textColor
        if (newTextColor == undefined) {
            newTextColor = "#243239";
            $(".chapter-actions button").removeClass('btn-secondary').addClass('btn-default');
        } else {
            $(".chapter-actions button").removeClass('btn-default').addClass('btn-secondary');
        }
        // Change background color
        setBackgroundColor(newBgColor);
        // Change color of everything with class .text-color
        setElementsColor(newTextColor);

        // Store the color to cookie and get them to load init pages
        Cookies.set('textColor', newTextColor);
        Cookies.set('backgroundColor', newBgColor);
    });


    var lazy_param = {
        scrollDirection: 'vertical',
        effect: 'fadeIn',
        effectTime: 200,
        chainable: false,
        threshold: 0,
        visibleOnly: true,
        onError: function (element) {
            element.attr("src", "/static/images/default.png")
        }
    };
    $('.lazyload').Lazy(lazy_param);
});