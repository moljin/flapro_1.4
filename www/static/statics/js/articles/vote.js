"use strict"
/*jshint esversion: 6 */
articleVoteInit();
function articleVoteInit(){
    let articleIdTag = document.querySelector("#article-id");
    const flashAlert_div = document.querySelector(".vote-alert");
    const voteBtn = document.querySelector("#vote-btn");
    if (voteBtn) {
        let article_id = articleIdTag.value;
        voteBtn.addEventListener('click', function (e) {
            e.preventDefault();
            let user_email_select = document.querySelector("[name='user_email']");
            let _url = articleVoteAjax;
            let _type = "article";
            let formData = new FormData();
            formData.append("article_id", article_id);
            if (user_email_select) { //어드민단
                formData.append("user_email", user_email_select.value);
            }
            AjaxUtils.voteRequest(_url, formData, flashAlert_div, _type, article_id);
        }, false);
    }

    const voteCancelBtn = document.querySelector("#vote-cancel-btn");
    if (voteCancelBtn) {
        let article_id = articleIdTag.value;
        voteCancelBtn.addEventListener('click', function (e) {
            e.preventDefault();
            voteCancelBtn.removeAttribute("hidden");
            AjaxUtils.articleVoteCancelFunc(article_id, null);
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
                    let article_id = Number(checkBox.getAttribute("id"));
                    let user_id = Number(checkBox.getAttribute("data-user-id"));
                    AjaxUtils.articleVoteCancelFunc(article_id, user_id);
                }
            });
        });
    }
}