"use strict"
/*jshint esversion: 6 */
emailInit();

function emailInit() {
    const emailAlert = document.querySelector(".email-alert");

    const upperEmailContainer = document.querySelector(".tab-container.upper .email");
    const lowerEmailContainer = document.querySelector(".tab-container.lower .email");

    const emailTokenBtn = lowerEmailContainer.querySelector('#email-token-btn');
    const emailConfirmBtn = document.querySelector(".btn.email");

    emailTokenBtn.addEventListener("click", function (e) {
        e.preventDefault();
        let email = lowerEmailContainer.querySelector("#email").value;
        let add_if = document.querySelector("#add_if").value;
        AjaxUtils.tokenCreate(email, add_if, emailAlert);
    }, false);

    emailConfirmBtn.addEventListener("click", function (e){
        let token = lowerEmailContainer.querySelector("#token").value;
        let formData = new FormData();
        formData.append("token", token);

        let request = $.ajax({
            url: tokenConfirmAjax,
            type: 'POST',
            data: formData,
            headers: {"X-CSRFToken": CSRF_TOKEN,},
            dataType: 'json',
            async: false,
            cache: false,
            contentType: false,
            processData: false,

            success: function (response) {
                if (response.error) {
                    AjaxUtils.responseErrorAlert(request, response);
                } else {
                    if (response.flash_message) {
                        AlertUtils.alertDisplay(emailAlert, response.flash_message);
                    }
                    if (response._success) {
                        AlertUtils.alertRemove(emailAlert);

                        let email = lowerEmailContainer.querySelector("#email").value;
                        let _id = document.querySelector("#user_id").value;
                        let formData = new FormData();
                        formData.append("email", email);
                        formData.append("user_id", _id);
                        let url = emailUpdateAjax;
                        let type = "successRedirect";
                        AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, null, type, null);
                    }

                }
            },
            error: function (err) {
                AjaxUtils.serverErrorAlert(err);
            }
        });
    }, false);
}