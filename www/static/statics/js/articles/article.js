"use strict"
/*jshint esversion: 6 */
articleInit();
function articleInit(){
    try { // article thumbnail single image
        let _width = ``;
        let _height = ``;

        let imgInput = document.querySelector('#image');
        let previewImgTag = document.querySelector('#img-preview');
        const existingImagePath = document.getElementById("img-preview").getAttribute("src");
        ImageUtils.eachImagePreview(_width, _height, imgInput, previewImgTag, existingImagePath, null, null);

    } catch (e) {
        console.log("");
    }

    try { // user article detail delete
        const articleDeleteBtn = document.querySelector("#article-delete-modal .user-btn");
        articleDeleteBtn.addEventListener("click", function (e) {
            e.preventDefault();
            let _id = document.querySelector("#article_id").value;
            articleDelete(_id, null);
        }, false);
    } catch (e) {
        console.log("");
    }

    /*#################################### admin ####################################*/
    try { // admin article detail delete
        // 선택자를 user 와는 다르게 잡았다.
        const articleDeleteBtn = document.querySelector("#article-delete-btn");
        const relatedAllDeleteCheck = document.querySelector("#related-all-delete");
        articleDeleteBtn.addEventListener('click', function (e) {
            e.preventDefault();
            let _id = document.querySelector("#article_id").value;
            articleDelete(_id, relatedAllDeleteCheck);

        }, false);
    } catch (e) {
        console.log("");
    }

    // try {  //admin article detail list check delete
    othersScript.checkBoxCheck();
    othersScript.realDataBoxCheck();

    const checkedDeleteBtn = document.querySelector("#checked-delete-btn");
    const checkBoxList = document.querySelectorAll("input.single");
    const relatedDataBoxList = document.querySelectorAll("input.data");
    if (checkedDeleteBtn) {
    checkedDeleteBtn.addEventListener("click", function (e) {
        e.preventDefault();
        Array.from(checkBoxList).forEach(function (checkBox, idx) {
            let relatedDataBoxCheck = relatedDataBoxList[idx];
            if (checkBox.checked) {
                let _id = Number(checkBox.getAttribute("id"));
                articleDelete(_id, relatedDataBoxCheck);
            }
        });
    });
    }



    // } catch (e) {
    //     console.log("");
    // }

    try { // admin article detail delete
        // 선택자를 user 와는 다르게 잡았다.
        const articleCommentDeleteBtn = document.querySelector("#comment-delete-btn");
        articleCommentDeleteBtn.addEventListener('click', function (e) {
            e.preventDefault();
            let _id = document.querySelector("#comment_id").value;
            articleCommentDelete(_id);

        }, false);
    } catch (e) {
        console.log("");
    }

    //admin article_comment detail list check delete
    const commentCheckAllBox = document.querySelector("#all-check");
    const commentCheckBoxList = document.querySelectorAll("input.single");
    if (commentCheckAllBox && commentCheckBoxList) {
        othersScript.checkBoxChange(commentCheckAllBox, commentCheckBoxList);
    }

    const commentCheckedDeleteBtn = document.querySelector("#comment-checked-delete-btn");
    if (commentCheckedDeleteBtn) {
        commentCheckedDeleteBtn.addEventListener("click", function (e) {
            e.preventDefault();
            Array.from(commentCheckBoxList).forEach(function (checkBox, idx) {
                if (checkBox.checked) {
                    let _id = Number(checkBox.getAttribute("id"));
                    articleCommentDelete(_id);
                }
            });
        });
    }


}

function articleDelete(_id, relatedAllDeleteCheck) {
    let relatedAll;
    if (relatedAllDeleteCheck) {
        relatedAll = relatedAllDeleteCheck.checked;
    }
    let url = articleDeleteAjax;
    let formData = new FormData();
    formData.append("article_id", _id);
    if (typeof relatedAll !== "undefined") {
        formData.append("related_all_delete", relatedAll);
    }
    let type = "successRedirect";
    AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, null, type, null);
}


function articleCommentDelete(_id) {
    let url = articleCommentDeleteAjax;
    let formData = new FormData();
    formData.append("comment_id", _id);
    let type = "successRedirect";
    AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, null, type, null);
}