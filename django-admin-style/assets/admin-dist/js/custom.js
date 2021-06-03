$(document).ready(function () {
    $('select').addClass("custom-select");
    let td_checkbox = $("td.action-checkbox input[type='checkbox'], td.delete input[type='checkbox'], " +
        "th.action-checkbox-column input[type='checkbox'], .checkbox-row input[type='checkbox'], .checkbox-row input[type='password']");
    $.each(td_checkbox, function (i) {
        $(this).addClass("custom-control-input");
        let next = $(this).next();
        if (next[0] !== undefined && next[0].nodeName === "LABEL") {
            next.attr({"class": ""}).addClass("custom-control-label");
            $(this).parent().wrap('<div class="custom-control custom-switch"></div>');
        } else {
            let id = $(this).attr("id");
            if (id === undefined || id === null) {
                id = "chk" + $(this).val();
                $(this).attr("id", id);
            }
            $(this).wrap('<div class="custom-control custom-switch"></div>');
            $(this).after('<label class="custom-control-label" for="' + id + '"></label>');
        }
    });

    let submit = $(".submit-row:not(.inline_actions) input[type='submit'], #content input[type='submit'], #changelist-search input[type='submit']");
    $.each(submit, function (i) {
        let val = $(this).val();
        let status = "success";
        let icon = "fa fa-save";

        if (!$(this).hasClass("default")) {
            if (val === yes_im_sure_text) {
                status = 'danger';
                icon = 'fa-trash-alt'
            } else if (val === search_text) {
                status = 'light';
                icon = 'fa-search'
            } else {
                status = 'light';
                icon = 'fa-arrow-alt-circle-right'
            }
        }
        $(this).replaceWith("<button type='submit' class='btn btn-" + status + "'><i class='fas " + icon + "'></i> " + val + "</button>");
    });
    $.each($('a.cancel-link, a.deletelink'), function (i) {
        let text = $(this).text();
        let status = "light";
        let icon = "fa fa-times";
        if ($(this).hasClass("deletelink")) {
            status = 'danger';
            icon = 'fa-trash-alt'
        }
        $(this).removeAttr("class");
        $(this).html("<button type='button' class='btn btn-" + status + "'><i class='fas " + icon + "'></i> " + text + "</button>")
    });
    $.each($(".actions button[type='submit']"), function (i) {
        $(this).removeClass("button").addClass("btn btn-light");
    });
    $.each($(".auth-form-group-custom input"), function (i) {
        $(this).addClass("form-control");
    });
    $.each($(".errornote"), function (i) {
        let text = $(this).text();
        $(this).replaceWith('<div class="alert alert-danger alert-dismissible fade show" role="alert">' + text +
            '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
            '<span aria-hidden="true">×</span></button></div>');
    });
});