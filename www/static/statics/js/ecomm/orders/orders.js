 "use strict"
 /*jshint esversion: 6 */

document.addEventListener('DOMContentLoaded', function () {
    const cancelPayBtn = document.querySelector("#cancel-pay");
    if (cancelPayBtn) {
        cancelPayBtn.addEventListener("click", function (e) {
            const merchant_uid = document.querySelector("#merchant-uid").value;
            const cancel_amount = document.querySelector("#cancel-amount").value;
            const pay_type = document.querySelector("#pay-type").value;
            const cancel_reason = document.querySelector("#cancel-reason").value;
            /* // 추후 가상계좌/계좌이체 사용시 추가
            const refund_holder = document.querySelector("#refund-holder").value;
            const refund_bank = document.querySelector("#refund-bank").value;
            const refund_account = document.querySelector("#refund-account").value;
            */
            let formData = new FormData();
            formData.append("merchant_uid", merchant_uid);
            formData.append("cancel_amount", cancel_amount);
            formData.append("pay_type", pay_type);
            formData.append("cancel_reason", cancel_reason);
            /* // 추후 가상계좌/계좌이체 사용시 추가
            formData.append("refund_holder", refund_holder);
            formData.append("refund_bank", refund_bank);
            formData.append("refund_account", refund_account);
            */
            let request = $.ajax({
                url: cancelPayAjax,
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
                        if (response._success === "success") {
                            const flashAlert_div = document.querySelector(".cancel-pay-alert");
                            AlertUtils.alertDisplay(flashAlert_div, response.flash_message);

                            const closeBtn = document.querySelector(".cancel-pay-alert .flashes .uk-alert-close");
                            closeBtn.addEventListener("click", function (e) {
                                flashAlert_div.style.display = "none";
                            }, false);
                            // flash 로 변경함
                            window.location.reload();
                        }
                        console.log("success", response._success);
                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        }, false);
    }

    const orderDeleteBtn = document.querySelector("#order-delete-btn");
    if (orderDeleteBtn) {
        orderDeleteBtn.addEventListener("click", function (e){
            const orderId = document.querySelector("#order-id").value;
            orderDelete(orderId);
        },false);
    }

    othersScript.checkBoxCheck();

    const checkedDeleteBtn = document.querySelector("#checked-delete-btn");
    const checkBoxList = document.querySelectorAll("input.single");
    if (checkedDeleteBtn) {
        checkedDeleteBtn.addEventListener("click", function (e) {
            e.preventDefault();
            Array.from(checkBoxList).forEach(function (checkBox) {
                if (checkBox.checked) {
                    let _id = Number(checkBox.getAttribute("id"));
                    orderDelete(_id);
                }
            });
        });
    }

});

function orderDelete (_id) {
    let _url = orderDeleteAjax;
    let _type = "successRedirect";
    let formData = new FormData();
    formData.append("order_id", _id);
    AjaxUtils.flashMessageRedirectRemoveDiv(_url, formData, null, _type, null);
}