$(document).ready(function (e) {
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
        $("#mobile-menu-action").prop("checked", false);
        $("#mobile-menu").css({
            "position": "",
            "top": "",
        });
        $("body").css({"overflow": ""});
    });
});