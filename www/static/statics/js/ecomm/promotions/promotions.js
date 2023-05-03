"use strict"
/*jshint esversion: 6 */
promotionsInit();
function promotionsInit(){
    const couponCodeCheckBtn = document.querySelector("#coupon-code-check-btn");
    couponCodeCheckBtn.addEventListener('click', function (e) {
        e.preventDefault();
        let user_id = document.querySelector("#user_id").value;
        let coupon_id = document.querySelector("#coupon_id").value;
        let code = document.querySelector("#code").value;

        let formData = new FormData();
        formData.append("user_id", user_id);
        formData.append("coupon_id", coupon_id);
        formData.append("code", code);
        let request = $.ajax({
            url: couponCodeCheckAjax,
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
                    const flashAlert_div = document.querySelector(".code-check-alert");
                    flashAlertDivInnerHtml(flashAlert_div, response);

                    const closeBtn = document.querySelector(".code-check-alert .flashes .uk-alert-close");
                    flashAlertDivDisplayNone (flashAlert_div, closeBtn);

                }
            },
            error: function (err) {
                AjaxUtils.serverErrorAlert(err);
            }
        });
    }, false);

}

function flashAlertDivInnerHtml (flashAlert_div, response) {
    if (response.flash_message) {
        flashAlert_div.style.display = "block";
        flashAlert_div.innerHTML = `<div class="flashes" uk-alert id="check-alert">
                                                        <div class="alert alert-danger" role="alert">` + response.flash_message + `</div>
                                                        <button class="uk-alert-close mt-5" type="button" uk-close></button></div>`
    } else {
        flashAlert_div.innerHTML = `<div class="flashes" uk-alert id="check-alert">
                                                        <div class="alert alert-danger" role="alert">사용 가능합니다.</div>
                                                        <button class="uk-alert-close mt-5" type="button" uk-close></button></div>`
    }
}

function flashAlertDivDisplayNone (flashAlert_div, closeBtn) {
    closeBtn.addEventListener("click", function (e) {
        flashAlert_div.style.display = "none";
    }, false);
}

