"use strict"
/*jshint esversion: 6 */
registerInit();
function registerInit(){
    const flashesContainer = document.querySelector(".form-container.register .flashes-container");
    const registerAlert = document.querySelector(".register-alert");
    const btnCheck = document.querySelector(".btn.check");
    const btnEmail = document.querySelector(".btn.email");
    const btnSign = document.querySelector(".btn.sign");
    const btnRegister = document.querySelector(".btn.register-btn");

    const upperCheckContainer = document.querySelector(".tab-container.upper .check-container");
    const upperEmailContainer = document.querySelector(".tab-container.upper .email-container");
    const upperSignContainer = document.querySelector(".tab-container.upper .sign-container");

    const lowerCheckContainer = document.querySelector(".tab-container.lower .check-container");
    const lowerEmailContainer = document.querySelector(".tab-container.lower .email-container");
    const lowerSignContainer = document.querySelector(".tab-container.lower .sign-container");

    const btnContainer = document.querySelector(".btn-container");

    const isAllCheckBox = lowerCheckContainer.querySelector(".all.uk-checkbox");
    const isCheckBoxList = lowerCheckContainer.querySelectorAll(".single.uk-checkbox");
    const isRequiredCheckBoxList = lowerCheckContainer.querySelectorAll(".single.required.uk-checkbox");

    const tokenBtn = lowerEmailContainer.querySelector('#token-btn');
    const signBtn = btnSign.querySelector("button");

    othersScript.checkBoxChange(isAllCheckBox, isCheckBoxList);

    btnCheck.addEventListener("click", function (e){
        const target = e.target;
        btnCheck.style.display = "none";
        btnEmail.style.display = "block";
        btnEmail.querySelector("button").innerHTML = "다음";
        btnSign.style.display = "none";
        btnRegister.style.display = "none";

        upperCheckContainer.style.display = "block";
        upperEmailContainer.style.display = "none";
        upperSignContainer.style.display = "none";

        lowerCheckContainer.style.display = "block";
        lowerEmailContainer.style.display = "none";
        lowerSignContainer.style.display = "none";
    }, false);

    btnEmail.addEventListener("click", function (e){
        if (flashesContainer) {
            AlertUtils.alertRemove(flashesContainer);
        }
        const target = e.target;
        let requiredCheckCount = 0;
        isRequiredCheckBoxList.forEach(function (requiredCheckBox, idx) {
            if (requiredCheckBox.checked === true) {
                requiredCheckCount++;
            }

            if (requiredCheckCount !== isRequiredCheckBoxList.length) {
                const message = "필수항목은 체크해야 해요 . . .";
                AlertUtils.alertDisplay(registerAlert, message);
            }

            if (requiredCheckCount === isRequiredCheckBoxList.length) {
                AlertUtils.alertRemove(registerAlert);

                btnCheck.style.display = "block";
                btnCheck.querySelector("button").innerHTML = "이전";
                btnEmail.style.display = "none";
                btnSign.style.display = "block";
                btnRegister.style.display = "none";

                upperCheckContainer.style.display = "none";
                upperEmailContainer.style.display = "block";
                upperSignContainer.style.display = "none";

                lowerCheckContainer.style.display = "none";
                lowerEmailContainer.style.display = "block";
                lowerSignContainer.style.display = "none";
            }
        });

    }, false);

    tokenBtn.addEventListener("click", function (e){
        let email = lowerEmailContainer.querySelector("#email").value;
        let add_if = document.querySelector("#add_if").value;
        AjaxUtils.tokenCreate(email, add_if, registerAlert);
    }, false);

    btnSign.addEventListener("click", function (e){
        const target = e.target;

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
                        AlertUtils.alertDisplay(registerAlert, response.flash_message);
                    }
                    if (response._success) {
                        AlertUtils.alertRemove(registerAlert);

                        btnCheck.style.display = "none";
                        btnEmail.style.display = "block";
                        btnEmail.querySelector("button").innerHTML = "이전";
                        btnSign.style.display = "none";
                        btnRegister.style.display = "block";

                        upperCheckContainer.style.display = "none";
                        upperEmailContainer.style.display = "none";
                        upperSignContainer.style.display = "block";

                        lowerCheckContainer.style.display = "none";
                        lowerEmailContainer.style.display = "none";
                        lowerSignContainer.style.display = "block";
                    }

                }
            },
            error: function (err) {
                AjaxUtils.serverErrorAlert(err);
            }
        });

    }, false);

    btnRegister.addEventListener("click", function (e){
        let is_use = lowerCheckContainer.querySelector("#is_use").value;
        let is_info = lowerCheckContainer.querySelector("#is_info").value;
        let is_email = lowerCheckContainer.querySelector("#is_email").value;
        let is_bank = lowerCheckContainer.querySelector("#is_bank").value;
        let is_marketing = lowerCheckContainer.querySelector("#is_marketing").value;
        let is_third = lowerCheckContainer.querySelector("#is_third").value;
        let email = lowerEmailContainer.querySelector("#email").value;
        let username = lowerSignContainer.querySelector("#username").value;
        let password = lowerSignContainer.querySelector("#password").value;
        let repassword = lowerSignContainer.querySelector("#repassword").value;

        let formData = new FormData();
        formData.append("is_use", is_use);
        formData.append("is_info", is_info);
        formData.append("is_email", is_email);
        formData.append("is_bank", is_bank);
        formData.append("is_marketing", is_marketing);
        formData.append("is_third", is_third);
        formData.append("email", email);
        formData.append("username", username);
        formData.append("password", password);
        formData.append("repassword", repassword);
        let url = registerSaveAjax;
        let type = "requestGetParam";
        AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, registerAlert, type, null);
    }, false);
}