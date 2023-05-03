"use strict"
/*jshint esversion: 6 */

document.addEventListener('DOMContentLoaded', function () {
    let _width = ``;
    let _height = ``;

    // symbol image preview (이용자단 및 어드민단)
    let symbolImgInput = document.querySelector('#symbol-image');
    let symbolPreviewImgTag = document.querySelector('#symbol-preview');
    if (document.getElementById("symbol-preview")) {
    const existingSymbolImagePath = document.getElementById("symbol-preview").getAttribute("src");
        ImageUtils.eachImagePreview(_width, _height, symbolImgInput, symbolPreviewImgTag, existingSymbolImagePath, null, null);
    }

    // cover image preview(또한, ImageUtils.eachImagePreview 참고) and delete
    const inputTagList = document.querySelectorAll('input.cover-image');
    const coverImgPreviewTagList = document.querySelectorAll('.cover-preview');
    const existingDeleteBtnList = document.querySelectorAll(".existing-btn");
    if (inputTagList) {
        inputTagList.forEach(function (inputTag, idx){
            let coverImgPreviewTag = coverImgPreviewTagList[idx];
            let existingDeleteBtn = existingDeleteBtnList[idx];
            let existingImagePath = coverImgPreviewTagList[idx].getAttribute("src");
            ImageUtils.eachImagePreview(_width, _height, inputTag, coverImgPreviewTag, existingImagePath, existingDeleteBtn, null);

            if (existingDeleteBtn) {
                existingDeleteBtn.addEventListener("click", function (e) {
                    e.preventDefault();
                    let target = e.target;
                    if (target.classList.contains("existing-cover")) {
                        let modalAlert = document.querySelector(".modal-alert");
                        let coverImgSrc = coverImgPreviewTag.getAttribute('src');
                        let userId = document.querySelector("#user_id").value;
                        let shopId = document.querySelector("#shop_id").value;
                        let formData = new FormData();
                        formData.append('user_id', userId);
                        formData.append("shop_id", shopId);
                        const _url = shopCoverImageCheckAjax;
                        const _indexUrl = indexUrl;
                        if (coverImgSrc.includes("cover_images")) {
                            for (let i = 0; i < 6; i++) {
                                if (idx === i) {
                                    //forLoop 때문에 function 을 밖으로 뺐다.
                                    shopCoverImageCheckAjaxFunc(formData, i, coverImgSrc, _url, existingDeleteBtn, userId, shopId, coverImgPreviewTag, _indexUrl);
                                }
                            }
                        } else {
                            AlertUtils.alertDisplay(modalAlert, "해당이미지는 존재하지 않습니다.");
                        }
                    }
                }, false);
            }
        });
    }

    function shopCoverImageCheckAjaxFunc(formData, i, coverImgSrc, url, existingDeleteBtn, userId, shopId, coverImgPreviewTag, _indexUrl) {
        formData.append("cover_image_" + `${i + 1}`, "static" + coverImgSrc.split("static")[1]);
        let request = $.ajax({
            url: url,
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
                    if (response._checked === "OK") {
                        console.log(response._checked);

                        existingDeleteBtnList.forEach(function (deleteBtn, ix) {
                            if (deleteBtn.style.display === "none") {
                                deleteBtn.style.display = "block";
                            }
                        });

                        existingDeleteBtn.style.display = "none";
                        let deleteHtml = `<div class="response-container">
                                                정말로 "${i + 1}"번째 이미지를 삭제하시겠어요?
                                                <input type="hidden" id="user_id_` + userId + `" name="user_id" value="` + userId + `">
                                                <input type="hidden" id="shop_id_` + shopId + `" name="shop_id" value="` + shopId + `">
                                                <div class="btn mt-15"><button class="delete-confirm-btn uk-button uk-button-default" type="button">삭제</button></div>
                                            </div>`;
                        AlertUtils.alertDisplay(modalAlert, deleteHtml);

                        let alertCloseBtn = modalAlert.querySelector(".uk-alert-close");
                        alertCloseBtn.addEventListener("click", function (e) {
                            e.preventDefault();
                            existingDeleteBtn.style.display = "block";
                        }, false);

                        let deleteConfirmBtn = modalAlert.querySelector(".delete-confirm-btn");
                        deleteConfirmBtn.addEventListener("click", function (e) {
                            e.preventDefault();

                            let _url = shopCoverImageDeleteAjax;
                            let formData = new FormData();
                            formData.append('user_id', userId);
                            formData.append("shop_id", shopId);
                            formData.append("cover_image_" + `${i + 1}`, "static" + coverImgSrc.split("static")[1]);
                            let _type = "onlyFlashMessageOrWindowReload";
                            AjaxUtils.flashMessageRedirectRemoveDiv(_url, formData, modalAlert, _type, null);
                            coverImgPreviewTag.removeAttribute('src');
                            coverImgPreviewTag.setAttribute('src', _indexUrl + "static/statics/images/shop/shop_cover_image_" + `${i + 1}` + ".jpg");
                            existingDeleteBtn.style.display = "none"; // 이미 none 인 경우도 있겠지만... 이미지 바꿔치기 않고 바로 삭제하는 경우
                            existingDeleteBtn.innerHTML = "";
                            existingDeleteBtn.classList.remove("existing-cover");
                            existingDeleteBtn.classList.add("none");
                        }, false);
                    } else {
                        console.log(response._checked);
                        AlertUtils.alertDisplay(modalAlert, "이미지가 존재하지 않습니다.");
                    }
                }
            },
            error: function (err) {
                AjaxUtils.serverErrorAlert(err);
            }
        });
    }

    // shop title check (이용자단 and 어드민단)
    const modalAlert = document.querySelector(".modal-alert");
    const titleCheckBtn = document.querySelector("#title-check-btn");
    if (titleCheckBtn) {
        titleCheckBtn.addEventListener("click", function (e){
                e.preventDefault();
                let title = document.querySelector("#title").value;
                let user_id;
                if (document.querySelector("#user_id")) {
                    user_id = document.querySelector("#user_id").value;
                } else {
                    user_id = "";
                }
                let user_email;
                if (document.querySelector("[name='user_email']")) {
                    user_email = document.querySelector("[name='user_email']").value;
                } else {
                    user_email = "";
                }
                let shop_id;
                if (document.querySelector("#shop_id")) {
                    shop_id = document.querySelector("#shop_id").value;
                } else {
                    shop_id = "";
                }
                let formData = new FormData();
                formData.append("title", title);
                formData.append("user_id", user_id);
                formData.append("user_email", user_email);
                formData.append("shop_id", shop_id);
                let url = existingShopTitleCheckAjax;
                let type = "onlyFlashMessageOrWindowReload";
                AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, modalAlert, type, null);
            }, false);
    }

    //shop save
    const shopSaveBtn = document.querySelector("#shop-save-btn");
    if (shopSaveBtn) {
        shopSaveBtn.addEventListener("click", function (e) {
            e.preventDefault();
            let _url = shopSaveAjax;
            let userId = document.querySelector("#user_id").value;
            let shopId = document.querySelector("#shop_id").value;
            let title = document.querySelector("#title").value;
            let content = document.querySelector("#content").value;
            let availableDisplay = document.querySelector("#available_display").checked;
            let symbolImage = document.querySelector("#symbol-image").files[0];
            let coverImage1 = document.querySelector("#cover-image-1").files[0];
            let coverImage2 = document.querySelector("#cover-image-2").files[0];
            let coverImage3 = document.querySelector("#cover-image-3").files[0];
            let coverImage4 = document.querySelector("#cover-image-4").files[0];
            let coverImage5 = document.querySelector("#cover-image-5").files[0];
            let coverImage6 = document.querySelector("#cover-image-6").files[0];
            let formData = new FormData();
            formData.append('user_id', userId);
            formData.append("shop_id", shopId);
            formData.append('title', title);
            formData.append("content", content);
            formData.append('available_display', availableDisplay);
            formData.append("symbol_image", symbolImage);
            formData.append("cover_image_1", coverImage1);
            formData.append("cover_image_2", coverImage2);
            formData.append("cover_image_3", coverImage3);
            formData.append("cover_image_4", coverImage4);
            formData.append("cover_image_5", coverImage5);
            formData.append("cover_image_6", coverImage6);

            let request = $.ajax({
                url: _url,
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
                            AlertUtils.alertDisplay(modalAlert, response.flash_message);
                        }
                        if (response._save) {
                            AlertUtils.alertRemove(modalAlert);

                            /*tag_ac_set 이 serializable 되지 않아 그냥 리다이렉트로 변경했다.*/
                            // window.location.replace('/boards/articles/category/detail/' + response._id + '/' + response.slug);
                            window.location.replace(response.redirect_url);
                            document.querySelector("#category-save-modal").style.display = "none";
                        }

                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }

            });
        }, false);
    }

    // shop delete (어드민단 change 에서도 사용)
    const shopDeleteBtn = document.querySelector("#shop-delete-modal .btn");
    const relatedAllDeleteCheck = document.querySelector("#related-all-delete"); // 이용자단에서는 null
    console.log(relatedAllDeleteCheck)
    if (shopDeleteBtn) {
        shopDeleteBtn.addEventListener("click", function (e){
            e.preventDefault();
            let _url = shopDeleteAjax;
            let userId = document.querySelector("#user_id").value;
            let shopId = document.querySelector("#shop_id").value;
            shopDelete(_url, userId, shopId, relatedAllDeleteCheck);
        });
    }

    // product category 백단 check 후 Ajax 단에서 change(update), save, 백단 check 후 Ajax 단에서 delete
    const categoryLoopInnerList = document.querySelectorAll(".existing-category .loop-inner");
    const categoryContentList = document.querySelectorAll(".existing-category .loop-inner .content");
    const categoryIdList = document.querySelectorAll('[name="category_id"]');
    const categoryChangeBtnList = document.querySelectorAll(".category-change-btn");
    const categorySaveBtnList = document.querySelectorAll(".category-save-btn");
    const categoryDeleteBtnList = document.querySelectorAll(".category-delete-btn");
    const existingAlert = document.querySelector(".existing-alert");

    if (categoryChangeBtnList) {
        categoryChangeBtnList.forEach(function (changeBtn, idx){
            let categorySaveBtn = categorySaveBtnList[idx];
            let categoryContent = categoryContentList[idx];
            let categoryChangeBtn = categoryChangeBtnList[idx];
            let categoryDeleteBtn = categoryDeleteBtnList[idx];
            let categoryId = categoryIdList[idx];
            changeBtn.addEventListener("click", function (e){
                e.preventDefault();

                categoryDeleteBtn.style.display = "block";
                changeBtn.style.display = "none";
                categorySaveBtn.style.display = "block";
                AlertUtils.alertRemove(existingAlert);
                let _url = productCategoryChangecheckAjax;
                let userId = document.querySelector("#user_id").value;
                let shopId = document.querySelector("#shop_id").value;
                let _type = "flashMessageFlashHTML";
                let formData = new FormData();
                formData.append('user_id', userId);
                formData.append("shop_id", shopId);
                formData.append("category_id", categoryId.value);
                formData.append("check_type", "change");
                AjaxUtils.flashMessageFlashHTML(_url, formData, null, _type, categoryContent, categoryChangeBtn, categorySaveBtn);

            }, false);
        });
    }

    if (categorySaveBtnList) {
        categorySaveBtnList.forEach(function (saveBtn, idx){
            let categoryLoopInner = categoryLoopInnerList[idx];
            let categoryContent = categoryContentList[idx];
            let categorySaveBtn = categorySaveBtnList[idx];
            let categoryChangeBtn = categoryChangeBtnList[idx];
            let categoryDeleteBtn = categoryDeleteBtnList[idx];
            let categoryId = categoryIdList[idx];
            saveBtn.addEventListener("click", function (e){
                e.preventDefault();
                let categoryChangedTitle = categoryLoopInner.querySelector('input[name="title"]');
                let categoryChangedAvailable = categoryLoopInner.querySelector('input[name="available_display"]');
                let _url = productCategoryChangeSaveAjax;
                let userId = document.querySelector("#user_id").value;
                let shopId = document.querySelector("#shop_id").value;
                let _type = "flashMessageFlashHTML";

                categoryChangeBtn.style.display = "block";
                categoryDeleteBtn.style.display = "block";
                categorySaveBtn.style.display = "none";
                let formData = new FormData();
                formData.append('user_id', userId);
                formData.append("shop_id", shopId);
                formData.append("category_id", categoryId.value);
                formData.append("title", categoryChangedTitle.value);
                formData.append("available_display", categoryChangedAvailable.checked);
                AjaxUtils.flashMessageFlashHTML(_url, formData, existingAlert, _type, categoryContent, categoryChangeBtn, categorySaveBtn);
            }, false);
        });
    }

    if (categoryDeleteBtnList) {
        categoryDeleteBtnList.forEach(function (deleteBtn, idx) {
            let categoryLoopInner = categoryLoopInnerList[idx];
            let categoryDeleteBtn = categoryDeleteBtnList[idx];
            let categoryId = categoryIdList[idx];
            deleteBtn.addEventListener("click", function (e) {
                e.preventDefault();
                // let _url = productCategoryDeleteAjax;
                let _url = productCategoryChangecheckAjax;
                let userId = document.querySelector("#user_id").value;
                let shopId = document.querySelector("#shop_id").value;
                // let _type = "onlyFlashMessage";
                // categoryLoopInner.remove();
                let _type = "flashMessageFlashHTML";
                deleteBtn.style.display = "none";
                let formData = new FormData();
                formData.append('user_id', userId);
                formData.append("shop_id", shopId);
                formData.append("category_id", categoryId.value);
                // AjaxUtils.flashMessageRedirectRemoveDiv(_url, formData, existingAlert, _type, null);
                formData.append("check_type", "delete");
                AjaxUtils.flashMessageFlashHTML(_url, formData, existingAlert, _type, null, categoryDeleteBtn, categoryLoopInner);
                }, false);
        });
    }

    // category add (태그 일부는 어드민단에서도 사용됨)
    const categoryRegisterBtn = document.querySelector(".category-register-btn");
    let categoryNum = document.getElementsByClassName("category-num");
    let titleInput = document.getElementsByClassName("add-title");
    let displayInput = document.getElementsByClassName("add-available_display");
    let cancelBtn = document.getElementsByClassName("cancel-input-btn");

    const maxInputFields = 11;
    let addInputCount = 1;
    const addInputBtn = document.querySelector(".add-input-btn");
    const categoryContainer = document.querySelector(".category-container");
    const newInputCategory = `<div uk-alert><div><label class="category-num"></label><input type="hidden" name="category_id" value="none"></div>
                                <div class="mt-10"><input class="uk-input add-title" maxlength="200" minlength="1" name="title" placeholder="상품 카테고리 이름" required="required" type="text" value=""></div>
                                <div class="mt-10">노출 여부: <input checked="checked" class="add-available_display uk-checkbox ml-10" name="available_display" type="checkbox">
                                <button class="cancel-input-btn remove-input ml-7 uk-alert-close uk-close">취소 <i class="fas fa-folder-minus ml-7"></i></button></div></div>`;

    const lastAlert = `<div uk-alert>
                            <a class="uk-alert-close" uk-close></a>           
                            <div class="mt-10">더이상 추가 할수 없습니다.
                                <div class="mt-5">저장 혹은 추가취소(혹은 새로고침)후 다시 시작해주세요!</div>
                            </div>                        
                        </div>`;
    if (addInputBtn) {
        addInputBtn.addEventListener("click", function (e){
            e.preventDefault();
            categoryRegisterBtn.style.display = "block";
            categoryRegisterBtn.style.float = "right";
            if (((e.target === addInputBtn) || (e.target.parentElement === addInputBtn)) && (addInputCount < maxInputFields)) {
                addInputCount++;
                categoryContainer.insertAdjacentHTML('beforeend', newInputCategory);
                if (addInputCount === 11) {
                    categoryContainer.insertAdjacentHTML('beforeend', lastAlert);
                }
                for (let i = 0; i < titleInput.length; i++) {
                    categoryNum[i].innerHTML = "추가 "+(i+1)+"번째 카테고리";
                    if (i === 9) {
                        categoryNum[i].innerHTML = "마지막 "+(i+1)+"번째"+ "옵션";
                    }

                    titleInput[i].id = "category-title-" +(i);
                    displayInput[i].id = "category-available-" +(i);
                    /*displayInput value numbering ==> checked 를 확인한다.*/
                    displayInput[i].value = (i);

                    cancelBtn[i].id = "cancel-btn-" +(i);
                }
            }
        });
    }

    /*#################################### admin ####################################*/
    /*symbol image preview js 는 이용자단과 동일, 아래는 cover image preview*/
    const coverImageInputTagList = document.querySelectorAll('input.cover-image');
    const coverImagePreviewTagList = document.querySelectorAll('.cover-preview');
    coverImageInputTagList.forEach(function (inputTag, idx){
        let coverImagePreviewTag = coverImagePreviewTagList[idx];
        let existingImagePath = coverImagePreviewTagList[idx].getAttribute("src");
        ImageUtils.eachImagePreview(_width, _height, inputTag, coverImagePreviewTag, existingImagePath, null, null);
    });

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
                let _url = shopDeleteAjax;
                let userId = checkBox.getAttribute("data-user-id");
                let shopId = Number(checkBox.getAttribute("id"));
                shopDelete(_url, userId, shopId, relatedDataBoxCheck);
            }
        });
    });
    }

    const adminChangeBtnList = document.querySelectorAll(".admin-change-btn");
    if (adminChangeBtnList) {
        adminChangeBtnList.forEach(function (changeBtn, idx){
            changeBtn.addEventListener("click", function (e){
                let categoryId = changeBtn.getAttribute("data-id");
                let categoryTitle = document.querySelector('[id="existing-title-' + `${categoryId}` + '"]').value;
                let categoryDisplay = document.querySelector('[id="existing-available-' + `${categoryId}` + '"]').checked;
                let alertDiv = document.querySelector(".existing-alert");
                let _url = productCategoryChangeSaveAjax;
                let _type = "onlyFlashMessageOrWindowReload";
                let formData = new FormData();
                formData.append("category_id", categoryId);
                formData.append("title", categoryTitle);
                formData.append("available_display", categoryDisplay);
                AlertUtils.alertRemove(alertDiv);
                AjaxUtils.flashMessageRedirectRemoveDiv(_url, formData, alertDiv, _type, null);
            },false);
        });
    }

    const adminCategoryDeleteBtnList = document.querySelectorAll(".admin-category-delete-btn");
    if (adminCategoryDeleteBtnList) {
        adminCategoryDeleteBtnList.forEach(function (deleteBtn, idx){
            deleteBtn.addEventListener("click", function (e){
                e.preventDefault();
                let categoryId = deleteBtn.getAttribute("data-id");
                let alertDiv = document.querySelector(".existing-alert");
                let categoryLoopInner = document.querySelector(".old-"+categoryId);
                let deleteModal = document.querySelector('[id="admin-category-delete-modal-' + `${categoryId}` + '"]');
                let _url = productCategoryDeleteAjax;
                let _type = "flashMessageRemoveDiv";
                let formData = new FormData();
                formData.append("category_id", categoryId);
                AlertUtils.alertRemove(alertDiv);
                AjaxUtils.flashMessageRedirectRemoveDiv(_url, formData, alertDiv, _type, categoryLoopInner);
                deleteModal.remove();
            },false);
        });
    }

    const addBtn = document.querySelector(".add-btn");
    const addCategory = `<div class="loop-inner new mt-10" uk-alert>
                            <a class="uk-alert-close" uk-tooltip="title: 추가취소; pos: bottom" uk-close></a>
                            <div class="content">
                                <div class="title uk-width-expand">
                                    <input class="add-title uk-input mt-5" maxlength="200" minlength="1" name="category_title" placeholder="상품 카테고리" required="required" type="text" value="">
                                </div>
                                <div class="content-inner">
                                    <div class="available ml-15">노출 여부:
                                        <input type="checkbox" class="add-available_display uk-checkbox ml-10" name="category_available_display" checked="checked">
                                    </div>  
                                </div>                              
                            </div>                            
                        </div>`;
    if (addBtn) {
        addBtn.addEventListener("click", function (e){
            e.preventDefault();
            if (addInputCount < maxInputFields) {
                addInputCount++;
                categoryContainer.insertAdjacentHTML('beforeend', addCategory);
                if (addInputCount === 11) {
                    categoryContainer.insertAdjacentHTML('beforeend', lastAlert);
                }
                for (let i = 0; i < titleInput.length; i++) {
                    titleInput[i].id = "category-title-" +(i);
                    displayInput[i].id = "category-available-" +(i);
                    /*displayInput value numbering ==> checked 를 확인한다.*/
                    displayInput[i].value = (i);
                }
            }
        },false);
    }

});


function shopDelete(_url, userId, shopId, relatedAllDeleteCheck) {
    let relatedAll;
    if (relatedAllDeleteCheck) {
        relatedAll = relatedAllDeleteCheck.checked;
    }
    let _type = "successRedirect";
    let formData = new FormData();
    formData.append('user_id', userId);
    formData.append("shop_id", shopId);
    if (typeof relatedAll !== "undefined") {
        formData.append("related_all_delete", relatedAll);
    }
    AjaxUtils.flashMessageRedirectRemoveDiv(_url, formData, null, _type, null);
}
