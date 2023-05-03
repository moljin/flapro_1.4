"use strict"
/*jshint esversion: 6 */
productVoteInit();
function productVoteInit(){
    let productIdTag = document.querySelector("#pd-id");
    const flashAlert_div = document.querySelector(".vote-alert");
    const voteBtn = document.querySelector("#vote-btn");
    if (voteBtn) {
        let product_id = productIdTag.value;
        voteBtn.addEventListener('click', function (e) {
            e.preventDefault();
            let user_email_select = document.querySelector("[name='user_email']");
            let _url = productVoteAjax;
            let _type = "product";
            let formData = new FormData();
            formData.append("product_id", product_id);
            if (user_email_select) { //어드민단
                formData.append("user_email", user_email_select.value);
            }
            AjaxUtils.voteRequest(_url, formData, flashAlert_div, _type, product_id);
        }, false);
    }

    const voteCancelBtn = document.querySelector("#vote-cancel-btn");
    if (voteCancelBtn) {
        let product_id = productIdTag.value;
        voteCancelBtn.addEventListener('click', function (e) {
            e.preventDefault();
            voteCancelBtn.removeAttribute("hidden");
            AjaxUtils.productVoteCancelFunc(product_id, null);
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
                    let product_id = Number(checkBox.getAttribute("id"));
                    let user_id = Number(checkBox.getAttribute("data-user-id"));
                    AjaxUtils.productVoteCancelFunc(product_id, user_id);
                }
            });
        });
    }
}