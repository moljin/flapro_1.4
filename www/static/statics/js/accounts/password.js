"use strict"
/*jshint esversion: 6 */
passwordInit();
function passwordInit(){
        const passwordAlert = document.querySelector(".password-alert");
        const upperPasswordContainer = document.querySelector(".tab-container.upper .password");
        const lowerPasswordContainer = document.querySelector(".tab-container.lower .password");
        const passwordSubmitBtn = document.querySelector(".btn.submit");

    const upperEmailContainer = document.querySelector(".tab-container.upper .email");
    const lowerEmailContainer = document.querySelector(".tab-container.lower .email");

    const passwordTokenBtn = lowerEmailContainer.querySelector('#password-token-btn');
    const passwordBtnEmail = document.querySelector(".btn.email");
    const btnPassword = document.querySelector(".btn.password");

    if (passwordBtnEmail) {
        passwordBtnEmail.addEventListener("click", function (e) {
            passwordBtnEmail.style.display = "none";
            btnPassword.style.display = "block";
            passwordSubmitBtn.style.display = "none";

            upperEmailContainer.style.display = "block";
            upperPasswordContainer.style.display = "none";

            lowerEmailContainer.style.display = "block";
            lowerPasswordContainer.style.display = "none";
        }, false);
    }

    if (passwordTokenBtn) {
        passwordTokenBtn.addEventListener("click", function (e) {
            let email = lowerEmailContainer.querySelector("#email").value;
            let add_if = document.querySelector("#add_if").value;
            AjaxUtils.tokenCreate(email, add_if, passwordAlert);
        }, false);
    }

    if (btnPassword) {
        btnPassword.addEventListener("click", function (e) {
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
                            AlertUtils.alertDisplay(passwordAlert, response.flash_message);
                        }
                        if (response._success) {
                            AlertUtils.alertRemove(passwordAlert);

                            passwordBtnEmail.style.display = "block";
                            passwordBtnEmail.querySelector("button").innerHTML = "이전";
                            btnPassword.style.display = "none";
                            passwordSubmitBtn.style.display = "block";

                            upperEmailContainer.style.display = "none";
                            upperPasswordContainer.style.display = "block";

                            lowerEmailContainer.style.display = "none";
                            lowerPasswordContainer.style.display = "block";
                        }

                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        }, false);
    }

    if (passwordSubmitBtn) {
        passwordSubmitBtn.addEventListener("click", function (e) {
            let password = document.querySelector("#password").value;
            let repassword = document.querySelector("#repassword").value;
            let _id = document.querySelector("#user_id").value;
            let formData = new FormData();
            formData.append("password", password);
            formData.append("repassword", repassword);
            formData.append("user_id", _id);
            let url = passwordSaveAjax;
            let type = "requestGetParam";
            AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, passwordAlert, type, null);
        }, false);
    }

}