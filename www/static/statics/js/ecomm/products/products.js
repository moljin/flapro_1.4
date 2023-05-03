"use strict"
/*jshint esversion: 6 */

document.addEventListener('DOMContentLoaded', function () {
    let _width;
    let _height;
    if (window.location.href.includes("admin")) {
        _width = ``;
        _height = ``;
    } else {
        _width = `100%`;
        _height = `auto`;
    }

    const thumbnailInputTagList = document.querySelectorAll('input.thumbnail');
    const thumbnailPreviewTagList = document.querySelectorAll('.preview-thumbnail');
    thumbnailInputTagList.forEach(function (inputTag, idx){
        let thumbnailPreviewTag = thumbnailPreviewTagList[idx];
        let existingImagePath = thumbnailPreviewTagList[idx].getAttribute("src");
        ImageUtils.eachImagePreview(_width, _height, inputTag, thumbnailPreviewTag, existingImagePath, null, null);
    });

    let optionNum = document.getElementsByClassName("op-num");
    let titleInput = document.getElementsByClassName("op-title-input");
    let priceInput = document.getElementsByClassName("op-price-input");
    let stockInput = document.getElementsByClassName("op-stock-input");
    let displayInput = document.getElementsByClassName("op-display-input");
    let orderInput = document.getElementsByClassName("op-order-input");
    let cancelBtn = document.getElementsByClassName("cancel-input-btn");

    const maxInputFields = 11;
    const addInputBtn = document.querySelector(".add-input-btn");
    const optionFormWrapper = document.querySelector(".option-form-wrapper");
    const newInputOption = `<div class="option-form" uk-alert>
                                <div class="board-form mt-10">
                                    <div class="form-group">
                                        <label class="op-num"></label>
                                        <input type="hidden" name="op_id" value="none">
                                    </div>
                                </div>
                                <div class="board-form mt-10">
                                    <div class="form-group">
                                        <input class="uk-input op-title-input mt-5" maxlength="100" minlength="2" name="op_title" placeholder="옵션이름" required="" type="text" value="">
                                    </div>
                                </div>
                                <div class="board-form mt-10">
                                    <div class="form-group">
                                        <input class="uk-input op-price-input mt-5" name="op_price" placeholder="옵션가격" required="" type="number" value="">
                                    </div>
                                </div>
                                <div class="board-form mt-10">
                                    <div class="form-group">
                                        <input class="uk-input op-stock-input mt-5" name="op_stock" placeholder="옵션재고" required="" type="number" value="">
                                    </div>
                                </div>
                                <div class="board-form mt-10">
                                    <div class="form-group">
                                        <label for="op_available_display">전시여부</label>
                                        <input checked class="uk-checkbox op-display-input mt-2 ml-5" name="op_available_display" type="checkbox">
                            
                                        &nbsp;/&nbsp;<label for="op_available_order">주문가능</label>
                                        <input checked class="uk-checkbox op-order-input mt-2 ml-5" name="op_available_order" type="checkbox">
                            
                                        <button class="cancel-input-btn remove-input ml-7 uk-alert-close uk-close">옵션취소 <i class="fas fa-folder-minus ml-7"></i></button>
                                    </div>
                                </div>
                            </div>`;

    const lastAlert = `<div class="option-form" uk-alert>
                            <a class="uk-alert-close" uk-close></a>           
                            <div class="mt-10">더이상 추가 할수 없습니다.
                                <div class="mt-5">저장 혹은 새로고침후 다시 시작해주세요!</div>
                                <div class="mt-5">(단, 최종적으로 등록할 수 있는 옵션수에는 제한이 없습니다.)</div>
                            </div>                        
                        </div>`;

    let addInputCount = 1;
    if (addInputBtn) {
    addInputBtn.addEventListener("click", function (e){
        e.preventDefault();
        if (((e.target === addInputBtn) || (e.target.parentElement === addInputBtn)) && (addInputCount < maxInputFields)) {
            addInputCount++;
            optionFormWrapper.insertAdjacentHTML('beforeend', newInputOption);
            if (addInputCount === 11) {
                    optionFormWrapper.insertAdjacentHTML('beforeend', lastAlert);
                }

            for (let i = 0; i < titleInput.length; i++) {
                optionNum[i].innerHTML = (i+1)+"번째 옵션";
                if (i===9) {
                    optionNum[i].innerHTML = "마지막 "+(i+1)+"번째"+ "옵션";
                }
                titleInput[i].id = "op-title-" +(i);
                priceInput[i].id = "op-price-" +(i);
                stockInput[i].id = "op-stock-" +(i);

                displayInput[i].id = "op-display-" +(i);
                /*displayInput value numbering ==> checked 를 확인한다.*/
                displayInput[i].value = (i);

                orderInput[i].id = "op-order-" +(i);
                /*orderInput value numbering ==> checked 를 확인한다.*/
                orderInput[i].value = (i);

                cancelBtn[i].id = "cancel-btn-" +(i);


            }
        }



    });
    }

    const productDeleteBtn = document.querySelector("#product-delete-btn");
    const relatedAllDeleteCheck = document.querySelector("#related-all-delete"); // 이용자단에서는 null
    if (productDeleteBtn) {
        productDeleteBtn.addEventListener("click", function (e) {
            e.preventDefault();
            let url = productDeleteAjax;
            let _id = document.querySelector("#pd-id").value;
            let user_id = document.querySelector("#user_id").value;
            productDelete(url, _id, user_id, relatedAllDeleteCheck);
        }, false);
    }

    /*############################### Admin select Function AND Product Delete ###############################*/
    const userEmailSelect = document.getElementById("user_email");
    if (userEmailSelect) {
        userEmailSelect.addEventListener("change", function (e){
            let selectedEmail = userEmailSelect.options[userEmailSelect.selectedIndex].value;
            let _url = userEmailSelectAjax;
            let _type = "admin_product_create";
            let formData = new FormData();
            formData.append("user_email", selectedEmail);
            formData.append("type", _type);
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
                        console.log("OK", response.shops)
                        const shopSelectTag = document.querySelector(".shop-select");

                        /*기존 선택회원 Shop 리스트 삭제하고...*/
                        othersScript.existingSelectDelete(shopSelectTag);

                        /*새롭게 선택되는 회원 Shop 리스트 추가하고...*/
                        othersScript.newSelectInsertIdTitle(shopSelectTag, response.shops);

                        for (let i = 0; i < response.shops.length; i++) {
                            console.log(response.shops[i].id);
                            console.log(response.shops[i].title);
                        }

                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        }, false);
    }

    const shopIdSelect = document.getElementById("shop_id");
    if (shopIdSelect) {
        shopIdSelect.addEventListener("change", function (e){
            let selectedShopId = shopIdSelect.options[shopIdSelect.selectedIndex].value;
            let _url = shopSelectAjax;
            let _type = "admin_product_create";
            let formData = new FormData();
            formData.append("shop_id", selectedShopId);
            formData.append("type", _type);
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
                        console.log("OK", response.categories)
                        const categorySelectTag = document.querySelector(".category-select");

                        /*기존 선택Shop 카테고리 리스트 삭제하고...*/
                        othersScript.existingSelectDelete(categorySelectTag);

                        /*새롭게 선택되는 Shop 카테고리 리스트 추가하고...*/
                        othersScript.newSelectInsertIdTitle(categorySelectTag, response.categories);

                        for (let i = 0; i < response.categories.length; i++) {
                            console.log(response.categories[i].id);
                            console.log(response.categories[i].title);
                        }

                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        }, false);
    }

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
                let _url = productDeleteAjax;
                let productId = Number(checkBox.getAttribute("id"));
                let userId = checkBox.getAttribute("data-user-id");
                productDelete(_url, productId, userId, relatedDataBoxCheck);
            }
        });
    });
    }


});

function productDelete(url, _id, user_id, relatedAllDeleteCheck) {
    let relatedAll;
    if (relatedAllDeleteCheck) {
        relatedAll = relatedAllDeleteCheck.checked;
    }
    let type = "successRedirect";
    let formData = new FormData();
    formData.append("_id", _id);
    formData.append("user_id", user_id);
    if (typeof relatedAll !== "undefined") {
        formData.append("related_all_delete", relatedAll);
    }
    AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, null, type, null);
}