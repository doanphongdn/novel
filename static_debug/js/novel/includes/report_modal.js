$(document).ready(function (e) {
    $('#report-form').on('submit', function (e) {
        e.preventDefault();
        let form_data = $(this).serializeArray();
        grecaptcha.execute(recaptcha_site_key, {action: 'submit'}).then(function (token) {
            form_data.push({name: 'g-recaptcha-response', value: $("*[name='g-recaptcha-response']").val()});
            $.ajax({
                type: "POST",
                url: "/novel/report",
                dataType: 'json',
                data: form_data,
                success: function (json_data) {
                    $('#modal-report').modal('toggle');
                    if (json_data.status) {
                        Swal.fire({
                            'text': json_data.message,
                            'icon':'success',
                        });
                    }
                }
            });
        });

    });
});