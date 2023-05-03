"use strict"
/*jshint esversion: 6 */
acSubscribeInit();

function acSubscribeInit() {
    let categoryIdTag = document.querySelector("#category-id");
    const flashAlert_div = document.querySelector(".subscribe-alert");
    const subscribeBtn = document.querySelector("#subscribe-btn");
    if (subscribeBtn) {
        let category_id = categoryIdTag.value;
        subscribeBtn.addEventListener('click', function (e) {
            e.preventDefault();
            let user_email_select = document.querySelector("[name='user_email']");
            let _url = acSubscribeAjax;
            let _type = "ac";
            let formData = new FormData();
            formData.append("category_id", category_id);
            if (user_email_select) { //어드민단
                formData.append("user_email", user_email_select.value);
            }
            AjaxUtils.subscribeRequest(_url, formData, flashAlert_div, _type, category_id);
        }, false);
    }

    const shopSubscribeCancelBtn = document.querySelector("#subscribe-cancel-btn");
    if (shopSubscribeCancelBtn) {
        let category_id = categoryIdTag.value;
        shopSubscribeCancelBtn.addEventListener('click', function (e) {
            e.preventDefault();
            AjaxUtils.acSubscribeCancelFunc(category_id, null);
        }, false);
    }

    // admin check delete
    othersScript.checkBoxCheck();

    const checkedDeleteBtn = document.querySelector("#checked-delete-btn");
    const checkBoxList = document.querySelectorAll("input.single");
    if (checkedDeleteBtn) {
        checkedDeleteBtn.addEventListener("click", function (e) {
            e.preventDefault();
            Array.from(checkBoxList).forEach(function (checkBox) {
                if (checkBox.checked) {
                    let category_id = Number(checkBox.getAttribute("id"));
                    let user_id = Number(checkBox.getAttribute("data-user-id"));
                    AjaxUtils.acSubscribeCancelFunc(category_id, user_id);
                }
            });
        });
    }
}