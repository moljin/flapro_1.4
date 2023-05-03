"use strict"
/*jshint esversion: 6 */
shopSubscribeInit();
function shopSubscribeInit() {
    let shopIdTag = document.querySelector("#shop-id");
    const flashAlert_div = document.querySelector(".shop-alert");
    const subscribeBtn = document.querySelector("#subscribe-btn");
    if (subscribeBtn) {
        let shop_id = shopIdTag.value;
        subscribeBtn.addEventListener('click', function (e) {
            e.preventDefault();
            let user_email_select = document.querySelector("[name='user_email']");
            let formData = new FormData();
            let _url = shopSubscribeAjax;
            let _type = "shop";
            formData.append("shop_id", shop_id);
            if (user_email_select) { //어드민단
                formData.append("user_email", user_email_select.value);
            }
            AjaxUtils.subscribeRequest(_url, formData, flashAlert_div, _type, shop_id);
        }, false);
    }

    const shopSubscribeCancelBtn = document.querySelector("#subscribe-cancel-btn");
    if (shopSubscribeCancelBtn) {
        let shop_id = shopIdTag.value;
        shopSubscribeCancelBtn.addEventListener('click', function (e) {
            e.preventDefault();
            AjaxUtils.shopSubscribeCancelFunc(shop_id, null);

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
                    let shop_id = Number(checkBox.getAttribute("id"));
                    let user_id = Number(checkBox.getAttribute("data-user-id"));
                    AjaxUtils.shopSubscribeCancelFunc(shop_id, user_id);
                }
            });
        });
    }
}