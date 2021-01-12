$(document).ready(function (e) {
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

    setInitAttrs();

});