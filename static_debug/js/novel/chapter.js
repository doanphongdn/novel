$(document).ready(function (e) {
    function setBackgroundColor(newBgColor) {
        // Change background of everything with class .bg-color
        $("body").css("background-color", newBgColor);
        $(".chapter-actions").css("background-color", newBgColor);
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

    function setInitAttrs() {
        // Color
        let textClor = Cookies.get('textColor');
        let bgColor = Cookies.get('backgroundColor');
        if (textClor) {
            setElementsColor(textClor);
        }
        if (bgColor) {
            // Remove class from currently active button
            $(".colors > li").removeClass("active-color");

            // Add class active to clicked button
            let currBgColorItem = $(".colors > li[data-color='" + bgColor + "']");
            $(currBgColorItem).addClass("active-color");

            setBackgroundColor(bgColor);
        }
        // Font size
        let fontSize = Cookies.get('fontSizeSlider');
        if (fontSize) {
            fontSizeSlider.noUiSlider.set(fontSize);
            setChapterFontSize(fontSize);
        }
        // Font Weight
        let fontWeight = Cookies.get('fontWeightSlider');
        if (fontWeight) {
            fontWeightSlider.noUiSlider.set(fontWeight);
            setChapterFontWeight(fontWeight);
        }
        // Line Height
        let lineHeight = Cookies.get('lineHeightSlider');
        if (lineHeight) {
            lineHeightSlider.noUiSlider.set(lineHeight);
            setChapterLineHeight(lineHeight);
        }
    }

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


    setInitAttrs();

    $(document).scroll(function () {
        var scrollTop = $(document).scrollTop();
        var contentTop = $('.chapter-content').offset().top;
        var menu = $('.chapter-actions');
        var menuWidth = menu[0].offsetWidth;
        diff = scrollTop - contentTop;
        if (diff > 0) {
            menu.css('width', menuWidth + "px");
            menu.css('position', "fixed");
            menu.css('box-shadow', "0 1px 10px rgba(50,50,93,.1),0 1px 5px rgba(0,0,0,.07)!important");
        } else {
            menu.css('position', "absolute");
            menu.css('width', "100%");
        }
    });

});