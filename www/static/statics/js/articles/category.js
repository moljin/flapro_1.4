"use strict"
/*jshint esversion: 6 */
articleCategoryInit();
function articleCategoryInit(){
    try { // Single cover image
        let _width = ``;
        let _height = ``;

        const coverImgInput = document.querySelector("#cover-image");
        let coverImgPreviewTag = document.querySelector('#cover-preview');
        const existingCoverImagePath = document.getElementById("cover-preview").getAttribute("src");
        ImageUtils.eachImagePreview(_width, _height, coverImgInput, coverImgPreviewTag, existingCoverImagePath, null, null);
    } catch (e) {
        console.log("");
    }

    try {  // user 의 ac_detail create
        const categoryAlert = document.querySelector(".category-alert");
        const titleCheckBtn = document.querySelector("#title-check-btn");
        const categorySaveBtn = document.querySelector("#category-save-btn");
        const acCoverImgDivTag = document.querySelector("#ac-img-path");
        const titleSpanTag = document.querySelector(".category > .title span.ac-title");
        const contentDivTag = document.querySelector(".category > div.content");
        const writerDivTag = document.querySelector(".category > div.writer > span");
        titleCheckBtn.addEventListener("click", function (e){
            e.preventDefault();
            let title = document.querySelector("#ac-title").value;
            let user_id = document.querySelector("#user-id").value;
            let user_email;
            if (document.querySelector("[name='user_email']")) {
                user_email = document.querySelector("[name='user_email']").value;
            } else {
                user_email = "";
            }
            console.log(user_email);
            let category_id = document.querySelector("#category-id").value;
            let formData = new FormData();
            formData.append("title", title);
            formData.append("user_id", user_id);
            formData.append("user_email", user_email);
            formData.append("category_id", category_id);
            let url = existingCategoryTitleCheckAjax;
            let type = "onlyFlashMessageOrWindowReload";
            AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, categoryAlert, type, null);
        }, false);

        categorySaveBtn.addEventListener("click", function (e){
            e.preventDefault();
            let user_id = document.querySelector("#user-id").value;
            let orm_id = document.querySelector("#orm-id").value;
            let category_id = document.querySelector("#category-id").value;
            let title = document.querySelector("#ac-title").value;
            let content = document.querySelector("#ac-content").value;
            let tagify = document.querySelector("#tagify").value;
            let availableDisplay = document.querySelector("#available_display").checked;
            let category_image = document.querySelector("#cover-image").files[0];
            let formData = new FormData();
            formData.append("user_id", user_id);
            formData.append("orm_id", orm_id);
            formData.append("category_id", category_id);
            formData.append("title", title);
            formData.append("content", content);
            formData.append("tagify", tagify);
            formData.append('available_display', availableDisplay);
            formData.append("image", category_image);
            let request = $.ajax({
                url: acSaveAjax,
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
                            AlertUtils.alertDisplay(categoryAlert, response.flash_message);
                        }
                        if (response._save) {
                            AlertUtils.alertRemove(categoryAlert);
                            if (response.ac_img_path) {
                                acCoverImgDivTag.setAttribute("data-src", "/" + response.ac_img_path);
                            }
                            titleSpanTag.innerHTML = response.ac_title;
                            contentDivTag.innerHTML = response.ac_content;
                            writerDivTag.innerHTML = response.nickname;

                            /*tag_ac_set 이 serializable 되지 않아 그냥 리다이렉트로 변경했다.*/
                            // window.location.replace('/boards/articles/category/detail/' + response._id + '/' + response.slug);
                            window.location.replace(response.redirect_url);

                            if (response._save === "create") {
                                let tagHtml = `<div class="board-form"></div>`;
                                document.querySelector(".cover-container .category").insertAdjacentHTML("beforeend", tagHtml);

                                document.querySelector("#category-id").value = response.ac_id;
                                let deleteModalLink = `<a href="#category-delete-modal" uk-toggle><span uk-icon="trash"></span></a>`;
                                let deleteModal = `<div id="category-delete-modal" class="uk-flex-top" uk-modal>
                                                        <div class="uk-modal-dialog uk-modal-body uk-margin-auto-vertical">
                                                            <button class="uk-modal-close-default" type="button" uk-close></button>
                                                            정말로 카테고리을 삭제하시겠어요?
                                                            <div class="btn uk-inline ml-15">
                                                                <button id="category-delete-btn" class="uk-button uk-button-primary uk-modal-close" type="button">삭제</button>
                                                            </div>
                                                        </div>
                                                    </div>`;
                                document.querySelector(".cover-container .category .uk-text-right").insertAdjacentHTML("beforeend", deleteModalLink);
                                document.querySelector(".cover-container .category").insertAdjacentHTML("afterend", deleteModal);

                                const categoryDeleteBtn = document.querySelector("#category-delete-btn");
                                categoryDeleteBtn.addEventListener("click", function (e) {
                                    e.preventDefault();
                                    const categoryId = document.querySelector("#category-id").value;
                                    categoryDelete(categoryId, categoryAlert);
                                }, false);
                            }
                            document.querySelector("#category-save-modal").style.display = "none";
                        }
                        if (response._err && response.res_msg) {
                            window.location.href = response.redirect_url + '?res_msg=' + response.res_msg;
                        }

                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        }, false);

        // user 의 ac_detail delete
        // 선택자를 admin 과는 다르게 잡았다.
        const userCategoryDeleteBtn = document.querySelector("#category-delete-modal .btn");
        if (userCategoryDeleteBtn) {
            userCategoryDeleteBtn.addEventListener("click", function (e) {
                e.preventDefault();
                const categoryId = document.querySelector("#category-id").value;
                categoryDelete(categoryId, null);
            }, false);
        }
    } catch (err) {
        console.log("");
    }

    /*#################################### admin ####################################*/
    // admin category detail delete
    // 선택자를 user 와는 다르게 잡았다.
    const adminCategoryDeleteBtn = document.querySelector("#category-delete-btn");
    const relatedAllDeleteCheck = document.querySelector("#related-all-delete");
    if (adminCategoryDeleteBtn) {
        adminCategoryDeleteBtn.addEventListener('click', function (e) {
            e.preventDefault();
            let categoryId = document.querySelector("#category-id").value;
            categoryDelete(categoryId, relatedAllDeleteCheck);

        }, false);
    }

    //admin category list check delete
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
                    categoryDelete(_id, relatedDataBoxCheck);
                }
            });

        });
    }

}


function categoryDelete(_id, relatedAllDeleteCheck) {
    let relatedAll;
    if (relatedAllDeleteCheck) {
        relatedAll = relatedAllDeleteCheck.checked;
    }
    let url = acDeleteAjax
    let formData = new FormData();
    formData.append("_id", _id);
    if (typeof relatedAll !== "undefined") {
        formData.append("related_all_delete", relatedAll);
    }
    let type = "successRedirect";
    AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, null, type, null);
}