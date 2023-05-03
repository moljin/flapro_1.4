"use strict"
/*jshint esversion: 6 */
cartInit();
const cartId = document.querySelector("#cart-id").value;
function cartInit () {

    // product count change
    const productContainerAll = document.querySelectorAll(".product.p-container");
    productContainerAll.forEach(function (productContainer){
        const productId = productContainer.getAttribute("data-product-id");
        const pdPlusBtn = document.querySelector('[id="pd-plus-' + `${productId}` + '"]');
        const pdMinusBtn = document.querySelector('[id="pd-minus-' + `${productId}` + '"]');
        const pd_type = "product";
        const pd_price = document.querySelector('[id="pd-applied-price-' + `${productId}` + '"]').value;
        cartPdPlusMinusInit(pd_type, pdPlusBtn, pdMinusBtn, productId, pd_price);
    });


    const productIdOptionSelectAll = document.querySelectorAll(".uk-select");
    productIdOptionSelectAll.forEach(function (optionSelect){
        // option select count change
        optionSelect.addEventListener("change", function (e){
            let dataProductId = optionSelect.getAttribute("data-product-id");
            const selectContainer = document.querySelector('[data-container-product-id="' + `${dataProductId}` + '"]');
            const opSelectInsertContainer = document.querySelector('[data-select-insert-pdid="' + `${dataProductId}` + '"]');
            e.preventDefault();
            let optionId = e.target.value;
            if (optionId !== "none") {
                let formData = new FormData();
                formData.append("_id", optionId);
                formData.append("_get", "get_option");
                let request = $.ajax({
                    url: optionSelectAjax,
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
                            if (response.pd_id && response._id && response._title && response._price) {
                                cartInsertSelectOption(optionSelect, opSelectInsertContainer, response.pd_id, response._id, response._title, response._price);
                                const opPlusBtn = document.querySelector('[data-plus-id="op-plus-' + `${response._id}` + '"]');
                                const opMinusBtn = document.querySelector('[data-minus-id="op-minus-' + `${response._id}` + '"]');
                                const _type = "option";
                                cartPdOpTotalPriceCalc(response.pd_id);
                                cartOpPlusMinusInit(_type, opPlusBtn, opMinusBtn, response.pd_id, response._id, response._price);

                                const orderChangeModal = document.querySelector('[id="order-change-modal-' + `${response.pd_id}` + '"]');
                                const productId = response.pd_id;//orderChangeModal.getAttribute("data-change-product-id");
                                let cartUpdateAjaxBtn = orderChangeModal.querySelector('[data-ajax-btn-id="' + `${productId}` + '"]');
                                cartUpdateAjax(cartUpdateAjaxBtn, productId);

                                const newOpCancelBtnAll = document.querySelectorAll(".new.op-cancel");
                                newOpCancelBtnAll.forEach(function (newOpCancelBtn, idx) {
                                    newOpCancelBtn.addEventListener("click", function (e) {
                                        console.log(newOpCancelBtn)
                                        const optionId = newOpCancelBtn.parentElement.getAttribute("data-option-id");
                                        const PdId = newOpCancelBtn.parentElement.getAttribute("data-insert-product-id");
                                        const hiddenTotalPriceInput = document.querySelector('[id="total-price-' + `${PdId}` + '"]');
                                        const TotalPriceSpan = document.querySelector('[class="total-price-' + `${PdId}` + '"]');

                                        const opTotalPrice = document.querySelector('[id="op-total-price-' + `${optionId}` + '"]').value;
                                        let oldTotalPrice = hiddenTotalPriceInput.value;

                                        if (idx === 0) { // loop 를 한번만 돌리기 위해서...합계금액을 두번 계산하기 때문
                                            hiddenTotalPriceInput.value = oldTotalPrice - opTotalPrice;
                                            TotalPriceSpan.innerHTML = othersScript.intComma(oldTotalPrice - opTotalPrice);
                                            // TotalPriceSpan.innerHTML = intComma(oldTotalPrice - opTotalPrice);
                                        }

                                    }, false);
                                });

                            }
                            if (response._data_r) {
                                console.log("data_r", response._data_r);
                            }
                        }
                    },
                    error: function (err) {
                        AjaxUtils.serverErrorAlert(err);
                    }
                });
            }

        });
    });

    const opSelectInsertAll = document.querySelectorAll(".op-select-insert");
    opSelectInsertAll.forEach(function (opSelectInsert){
        const productId = opSelectInsert.getAttribute("data-insert-product-id");
        const optionId = opSelectInsert.getAttribute("data-option-id");
        const opPlusBtn = document.querySelector('[data-plus-id="op-plus-' + `${optionId}` + '"]');
        const opMinusBtn = document.querySelector('[data-minus-id="op-minus-' + `${optionId}` + '"]');
        const _type = "option";
        const optionPrice = document.querySelector('[id="op-price-' + `${optionId}` + '"]').value;
        cartOpPlusMinusInit(_type, opPlusBtn, opMinusBtn, productId, optionId, optionPrice);
    });

    const cartProductTag = document.querySelector(".cart-product");
    const opSelectInsertContainer = document.querySelector(".op-select-insert-container");
    cartProductTag.addEventListener("click", function (e){
        const opSelectInsertAll = document.querySelectorAll(".op-select-insert");
        opSelectInsertAll.forEach(function (opSelectInsert, idx) {
            const optionId = opSelectInsert.getAttribute("data-option-id");
            let OpCancelBtn = opSelectInsert.querySelector('[data-cancel-id="' + `${optionId}` + '"]');
            OpCancelBtn.addEventListener("click", function (e) {
                console.log(OpCancelBtn)
                const PdId = OpCancelBtn.parentElement.getAttribute("data-insert-product-id");
                const optionId = OpCancelBtn.parentElement.getAttribute("data-option-id");
                let formData = new FormData();
                formData.append("cart_id", cartId);
                formData.append("product_id", PdId);
                formData.append("option_id", optionId);

                let request = $.ajax({
                    url: cartOptionDeleteAjax,
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
                            if (response.unnecessary_ajax) {
                                console.log(response.unnecessary_ajax);
                            }
                            if (response._success) {
                                const hiddenTotalPriceInput = document.querySelector('[id="total-price-' + `${PdId}` + '"]');
                                const TotalPriceSpan = document.querySelector('[class="total-price-' + `${PdId}` + '"]');

                                const opTotalPrice = document.querySelector('[id="op-total-price-' + `${optionId}` + '"]').value;
                                let oldTotalPrice = hiddenTotalPriceInput.value;

                                hiddenTotalPriceInput.value = oldTotalPrice - opTotalPrice;
                                TotalPriceSpan.innerHTML = othersScript.intComma(oldTotalPrice - opTotalPrice);
                                // TotalPriceSpan.innerHTML = intComma(oldTotalPrice - opTotalPrice);

                            }

                        }
                    },
                    error: function (err) {
                        AjaxUtils.serverErrorAlert(err);
                    }
                });
            }, false);
        });
    }, false);

    const cartProductContainerAll = document.querySelectorAll(".cart-product-container");
    cartProductContainerAll.forEach(function (cartProductContainer){
        const productId = cartProductContainer.getAttribute("data-cart-product-id");
        let cartUpdateAjaxBtn = cartProductContainer.querySelector('[data-ajax-btn-id="' + `${productId}` + '"]');
        cartUpdateAjax(cartUpdateAjaxBtn, productId);
    });

    const orderChangeModalAll = document.querySelectorAll(".order-change-modal");
    orderChangeModalAll.forEach(function (orderChangeModal, idx){
        let PdId = orderChangeModal.getAttribute("data-change-pd-id");
        const cartProductDeleteBtn = document.querySelector('[id="product-delete-btn-' + `${PdId}` + '"]');
        cartProductDeleteBtn.addEventListener("click", function (ev) {
            ev.preventDefault();

            cartProductDelete(cartId, PdId);
        }, false);

        // 카트에 담은 주문을 수정할 때 저장을 누르지 않고 나가는 경우에 대한 대비 , 이게 꼭 있어야 하나????
        // cartUpdateAjax(orderChangeModal, PdId);

    });

    othersScript.checkBoxCheck();
    const checkedDeleteBtn = document.querySelector("#checked-delete-btn");
    const checkAllBox = document.querySelector("#all-check");
    const checkBoxList = document.querySelectorAll("input.single");
    if (checkedDeleteBtn) {
    checkedDeleteBtn.addEventListener("click", function (e) {
        e.preventDefault();
        Array.from(checkBoxList).forEach(function (checkBox) {
            if (checkBox.checked) {
                let PdId = Number(checkBox.getAttribute("id"));
                cartProductDelete(cartId, PdId);
                checkAllBox.checked = false;
            }
        });
    });
    }

    try {
        // coupon  apply
        const couponApplyBtn = document.querySelector("#coupon-apply");
        couponApplyBtn.addEventListener("click", function (e) {
            e.preventDefault();
            const couponCode = document.querySelector("#coupon-code").value;

            let formData = new FormData();
            formData.append("cart_id", cartId);
            formData.append("code", couponCode);
            let request = $.ajax({
                url: addCouponAjax,
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
                        if (response.used_coupon_id) {
                            const usedCouponContainer = document.querySelector(".usedcoupon-container");
                            const usedCouponLabel = document.querySelector(".usedcoupon-container .label");
                            // usedCouponLabel.style.display = "flex";
                            const insertHtml = `<div class="each" id="each-` + response.used_coupon_id + `">
                                                <div class="code uk-width-expand">` + response.used_coupon_code + `
                                                    <span class="period"> &nbsp;(` + response.used_coupon_use_from + `~` + response.used_coupon_use_to + `)</span>
                                                </div>
                                                <div class="amount-button">
                                                    <div class="amount">` + othersScript.intComma(response.used_coupon_amount) + `원</div>
                                                    <div class="button">
                                                        <button class="uk-button uk-button-default coupon-cancel-btn" type="button" uk-toggle="target: #usedcoupon-cancel-modal-` + response.used_coupon_id + `" data-used-coupon-id="` + response.used_coupon_id + `">적용취소</button>
                                                    </div>
                                                </div>
                                            
                                                <div id="usedcoupon-cancel-modal-` + response.used_coupon_id + `" class="usedcoupon-cancel-modal uk-flex-top" data-usedcoupon-id="` + response.used_coupon_id + `" uk-modal>
                                                    <div class="uk-modal-dialog uk-modal-body uk-margin-auto-vertical">
                                                        <button class="uk-modal-close-default" type="button" uk-close></button>
                                                        쿠폰 적용을 취소하시겠어요?
                                                        <div class="btn uk-align-right">
                                                            <div class="uk-inline">
                                                                <button class="uk-button uk-button-default uk-modal-close" type="button">취소</button>
                                                            </div>
                                                            <div class="delete-btn uk-inline ml-15">
                                                                <button id="coupon-cancel-btn-` + response.used_coupon_id + `" class="uk-button uk-button-default uk-modal-close" type="button">삭제</button>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>`;
                            usedCouponContainer.insertAdjacentHTML('beforeend', insertHtml);

                            couponPointPayPriceInnerHtml(response);

                            const flashAlert_div = document.querySelector(".coupon-point-alert");
                            flashAlertDivInnerHtml(flashAlert_div, response);

                            const closeBtn = document.querySelector(".coupon-point-alert .flashes .uk-alert-close");
                            flashAlertDivDisplayNone(flashAlert_div, closeBtn);
                        } else {
                            const flashAlert_div = document.querySelector(".coupon-point-alert");
                            flashAlertDivInnerHtml(flashAlert_div, response);

                            const closeBtn = document.querySelector(".coupon-point-alert .flashes .uk-alert-close");
                            flashAlertDivDisplayNone(flashAlert_div, closeBtn);
                        }


                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        }, false);
    } catch (e) {
        // console.log(e);
    }

    try { // point apply
        const pointApplyBtn = document.querySelector("#point-apply");
         console.log("포인트 적용 pointApplyBtn", pointApplyBtn)
        pointApplyBtn.addEventListener("click", function (e) {
            e.preventDefault();
            console.log("포인트 적용 클릭")
            const usedPoint = document.querySelector("#used-point").value;

            let formData = new FormData();
            formData.append("cart_id", cartId);
            formData.append("used_point", usedPoint);
            let request = $.ajax({
                url: applyPointAjax,
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
                        if (response.point_log_id) {
                            console.log(response)
                            const appliedCpGroupTag = document.querySelector(".cp-group.applied");
                            appliedCpGroupTag.innerHTML = `<div class="point-log">
                                                            <div class="label">할인 적용포인트</div>
                                                            <input type="hidden" name="cart_point_log_id" value="` + response.point_log_id + `">
                                                            <div class="cancel" uk-grid>
                                                                <div><span id="applied-used-point">` + othersScript.intComma(response.used_point) + `</span>점</div>
                                                                <div class="button"><button type="button" class="uk-button uk-button-default point-cancel-btn" uk-toggle="target: #usedpoint-cancel-modal-` + response.point_log_id + `" data-point-log-id="` + response.point_log_id + `">적용취소</button></div>
                                                            </div>
                                                        </div>
                                                        <div id="usedpoint-cancel-modal-` + response.point_log_id + `" class="usedpoint-cancel-modal uk-flex-top" uk-modal>
                                                            <div class="uk-modal-dialog uk-modal-body uk-margin-auto-vertical">
                                                                <button class="uk-modal-close-default" type="button" uk-close></button>
                                                                포인트 적용을 취소하시겠어요?
                                                                <div class="btn uk-align-right">
                                                                    <div class="uk-inline">
                                                                        <button class="uk-button uk-button-default uk-modal-close" type="button">취소</button>
                                                                    </div>
                                                                    <div class="delete-btn uk-inline ml-15">
                                                                        <button id="point-cancel-btn-` + response.point_log_id + `" class="uk-button uk-button-default uk-modal-close" type="button">삭제</button>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>`;

                            couponPointPayPriceInnerHtml(response);

                            const flashAlert_div = document.querySelector(".coupon-point-alert");
                            flashAlertDivInnerHtml(flashAlert_div, response);

                            const closeBtn = document.querySelector(".coupon-point-alert .flashes .uk-alert-close");
                            flashAlertDivDisplayNone(flashAlert_div, closeBtn);
                        } else {
                            const flashAlert_div = document.querySelector(".coupon-point-alert");
                            flashAlertDivInnerHtml(flashAlert_div, response);

                            const closeBtn = document.querySelector(".coupon-point-alert .flashes .uk-alert-close");
                            flashAlertDivDisplayNone(flashAlert_div, closeBtn);
                        }


                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        }, false);
    } catch (e) {
        // console.log(e);
    }

    /*coupon cancel*/
    const usedCouponContainer = document.querySelector(".usedcoupon-container");
    usedCouponContainer.addEventListener("click", function (e){
        const usedCouponCancelModalAll = document.querySelectorAll(".usedcoupon-cancel-modal");
        usedCouponCancelModalAll.forEach(function (usedCouponCancelModal, idx) {
            let _id = usedCouponCancelModal.getAttribute("data-usedcoupon-id");
            let couponCancelBtn = document.querySelector('[id="coupon-cancel-btn-' + `${_id}` + '"]');
            couponCancelBtn.addEventListener("click", function (ev) {
                ev.preventDefault();
                let formData = new FormData();
                formData.append("cart_id", cartId);
                formData.append("_id", _id);

                let request = $.ajax({
                    url: cancelCouponAjax,
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
                            if (response.unnecessary_ajax) {
                                console.log(response.unnecessary_ajax);
                            }
                            if (response.flash_message) {
                                let eachUsedCouponTag = document.querySelector('[id="each-' + `${_id}` + '"]');
                                let usedCouponCancelModal = document.querySelector('[id="usedcoupon-cancel-modal-' + `${_id}` + '"]');
                                eachUsedCouponTag.remove();
                                usedCouponCancelModal.remove(); //each tag 안에 들어있어 굳이 삭제안해도 each 가 지워질때 지워진다.

                                const eachAll = document.querySelectorAll(".each");
                                const usedCouponSpan = document.querySelector(".usedcoupon-span");
                                if (eachAll.length === 0) {
                                    if (usedCouponSpan) {
                                        usedCouponSpan.remove();
                                    }
                                }

                                couponPointPayPriceInnerHtml(response);

                                const flashAlert_div = document.querySelector(".coupon-point-alert");
                                flashAlertDivInnerHtml(flashAlert_div, response);

                                const closeBtn = document.querySelector(".coupon-point-alert .flashes .uk-alert-close");
                                flashAlertDivDisplayNone(flashAlert_div, closeBtn);
                            }

                        }
                    },
                    error: function (err) {
                        AjaxUtils.serverErrorAlert(err);
                    }
                });
            }, false);

        });
    }, false);

    /*point cancel*/
    const usedPointContainer = document.querySelector(".usedpoint-container");
    usedPointContainer.addEventListener("click", function (e){
        let target = e.target;
        if (target.classList.contains("point-cancel-btn")) {
            // // ajax 중복호출 막기위해...
            if(isPromotionRun === true) {
                return;
            }
            isPromotionRun = true;
            let _id = target.getAttribute("data-point-log-id");
            let pointCancelBtn = document.querySelector('[id="point-cancel-btn-' + `${_id}` + '"]');
            pointCancelBtn.addEventListener("click", function (ev) {
                ev.preventDefault();
                let formData = new FormData();
                formData.append("cart_id", cartId);
                formData.append("cart_point_log_id", _id);

                let request = $.ajax({
                    url: cancelPointAjax,
                    type: 'POST',
                    data: formData,
                    headers: {"X-CSRFToken": CSRF_TOKEN,},
                    dataType: 'json',
                    async: false,
                    cache: false,
                    contentType: false,
                    processData: false,

                    success: function (response) {
                        isPromotionRun = false;
                        if (response.error) {
                            AjaxUtils.responseErrorAlert(request, response);
                        } else {
                            const pointLogTag = document.querySelector(".point-log");
                            const usedPointCancelModal = document.querySelector('[id="usedpoint-cancel-modal-' + `${_id}` + '"]');
                            pointLogTag.remove();
                            usedPointCancelModal.remove();

                            couponPointPayPriceInnerHtml(response);

                            const flashAlert_div = document.querySelector(".coupon-point-alert");
                            flashAlertDivInnerHtml(flashAlert_div, response);

                            const closeBtn = document.querySelector(".coupon-point-alert .flashes .uk-alert-close");
                            flashAlertDivDisplayNone (flashAlert_div, closeBtn);

                        }
                    },
                    error: function (err) {
                        AjaxUtils.serverErrorAlert(err);
                    }
                });
            }, false);

        }

    }, false);


}

// /*ajax 중복호출 막기위해... point cancel 에서 사용*/
let isPromotionRun = false;

function cartProductDelete(cartId, PdId){
    let formData = new FormData();
    formData.append("cart_id", cartId);
    formData.append("product_id", PdId);

    let request = $.ajax({
        url: cartProductDeleteAjax,
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
                pointAllPriceInnerHtml(response);
                pointCouponFlashTagRemove(response);

                const cartProductContainer = document.querySelector('[data-cart-product-id="' + `${PdId}` + '"]');
                if (cartProductContainer) {
                    cartProductContainer.remove();
                }

                const orderChangeModal = document.querySelector('[id="order-change-modal-' + `${PdId}` + '"]');
                if (orderChangeModal) {
                    orderChangeModal.remove();
                }
                const orderDeleteModal = document.querySelector('[id="order-delete-modal-' + `${PdId}` + '"]');
                if (orderDeleteModal) {
                    orderDeleteModal.remove();
                }

                const cartItemsCountSpan = document.querySelector(".header span.cart-items-count");
                const cartProductContainerAll = document.querySelectorAll(".cart-product-container");
                const orderFormDisplayBtn = document.querySelector(".order-form-display-btn ");
                const orderFormDiv = document.querySelector(("#order_form_div"));
                const cartProduct = document.querySelector(".cart-product.bg-100.padding10");
                cartItemsCountSpan.innerHTML = String(cartProductContainerAll.length);
                if (cartProductContainerAll.length === 0) {
                    orderFormDisplayBtn.remove();
                    orderFormDiv.remove();
                    let newDiv = `<div class="main-width mb-20">
                                     카트에 담긴게 없습니다.
                                  </div>`;
                    cartProduct.insertAdjacentHTML('afterbegin', newDiv);
                }

            }
        },
        error: function (err) {
            AjaxUtils.serverErrorAlert(err);
        }
    });


}

function cartUpdateAjax(cartUpdateAjaxBtn, pdId) {
    cartUpdateAjaxBtn.addEventListener("click", function (e) {
        console.log("cartUpdateAjax,,,, =============")
        e.preventDefault();
        // const pdId = cartUpdateAjaxBtn.getAttribute("data-ajax-btn-id");
        let orderChangeModal = document.querySelector('[data-change-pd-id="' + `${pdId}` + '"]');
        const opSelectInsertAll = orderChangeModal.querySelectorAll('[data-insert-product-id="' + `${pdId}` + '"]');

        const pdCount = document.querySelector('[id="pd-count-' + `${pdId}` + '"]').value;
        const pdTotalPrice = document.querySelector('[id="pd-total-price-' + `${pdId}` + '"]').value;

        let optionId = [];
        let optionCount = [];
        let optionTotalPrice = [];
        opSelectInsertAll.forEach(function (opSelectInsert, idx) {
            let opId = opSelectInsert.getAttribute("data-option-id");
            optionId.push(opId);//opSelectInsert.querySelector('[id="data-op-id-' + `${opId}` + '"]').value);
            optionCount.push(opSelectInsert.querySelector('[id="op-count-' + `${opId}` + '"]').value);
            optionTotalPrice.push(opSelectInsert.querySelector('[id="op-total-price-' + `${opId}` + '"]').value);
        });

        let formData = new FormData();
        formData.append("cart_id", cartId);
        formData.append("product_id", pdId);
        formData.append("product_count", pdCount);
        formData.append("product_total_price", pdTotalPrice);

        for (let i = 0; i < optionId.length; i++) {
            formData.append('option_id[]', optionId[i]);
            formData.append('option_count[]', optionCount[i]);
            formData.append('option_total_price[]', optionTotalPrice[i]);
        }

        let request = $.ajax({
            url: cartUpdatAjax,
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
                    const pdSubQtySpan = document.querySelector('[id="pd-sub-qty-' + `${pdId}` + '"]');
                    pdSubQtySpan.innerHTML = othersScript.intComma(response.pd_subtotal_qty);
                    const pdSubtotalPriceSpan = document.querySelector('[id="pd-subtotal-price-' + `${pdId}` + '"]');
                    pdSubtotalPriceSpan.innerHTML = othersScript.intComma(response.product_subtotal_price);
                    const opSubtotalPriceSpan = document.querySelector('[id="op-subtotal-price-' + `${pdId}` + '"]');
                    opSubtotalPriceSpan.innerHTML = othersScript.intComma(response.cartproduct_op_subtotal_price);
                    const pdLinePriceSpan = document.querySelector('[id="pd-line-price-' + `${pdId}` + '"]');
                    pdLinePriceSpan.innerHTML = othersScript.intComma(response.cartproduct_line_price);

                    const cartRtOpContent = document.querySelector('[id="op-content-' + `${pdId}` + '"]');
                    const cartRtOpFor = document.querySelector('[id="for-' + `${pdId}` + '"]');
                    let newHtml = document.createElement('DIV');
                    newHtml.setAttribute("id", "for-" + `${pdId}`);
                    for (let i = 0; i < response.op_id.length; i++) {
                        let cartOpItemHtml = `<div class="cartop-item">
                                            ${response.op_title[i]}(${othersScript.intComma(response.op_price[i])}원) 
                                            <span id="op-qty-` + response.op_id[i] + `">${response.op_count[i]}</span>개
                                          </div>`;
                        newHtml.insertAdjacentHTML('beforeend', cartOpItemHtml);
                    }
                    cartRtOpFor.remove();
                    cartRtOpContent.append(newHtml);

                    pointAllPriceInnerHtml(response);
                    pointCouponFlashTagRemove(response);

                }
            },
            error: function (err) {
                AjaxUtils.serverErrorAlert(err);
            }
        });

    }, false);
}

function cartInsertSelectOption (selectTag, div, pd_id, _id, title, price) {
    let oldInsertDiv = document.querySelector('[data-id="op-' + `${_id}` + '"]');
    if (oldInsertDiv) {
        alert("이미 선택한 옵션이에요!");
        selectTag.value = "none";
    }
    else {
        let newDiv = `<div class="new op-select-insert" data-option-id="${_id}" data-insert-product-id="${pd_id}" uk-alert>
                          <div class="op-title mb-10" data-id="op-${_id}">${title} / ${othersScript.intComma(Number(price))}원</div>
<!--                          <button class="new op-cancel uk-alert-close uk-close" type="button" data-cancel-id="${_id}">+</button>-->
                          <button class="new op-cancel uk-alert-close" data-cancel-id="${_id}" uk-close>취소</button>
                          <div>
                              <button class="uk-button uk-button-default op-minus" data-minus-id="op-minus-${_id}"><span uk-icon="minus"></span></button>
                              <input readonly class="uk-input uk-form-width-xsmall op" id="op-count-${_id}" name="op-count" type="text" value="1">
                              <input type="hidden" name="op-id" value="${_id}">
                              <input type="hidden" id="op-price-${_id}" value="${Number(price)}">
                              <input type="hidden" class="op-total-price" id="op-total-price-${_id}" name="op-total-price" value="${Number(price)}">
                              <button class="uk-button uk-button-default op-plus" data-plus-id="op-plus-${_id}"><span uk-icon="plus"></span></button>
                              <div class="uk-inline uk-align-right ml-0 mt-5 mb-0"><span id="op-total-price-span-${_id}">` + othersScript.intComma(Number(price)) + `</span> 원</div>
                          </div>
                     </div>`;
        div.insertAdjacentHTML('afterbegin', newDiv);
        selectTag.value = "none";

    }
}

function cartPdPlusMinusInit (_type, plusBtn, minusBtn, _id, price) {
    let countInput = document.querySelector('[id="pd-count-' + `${_id}` + '"]');
        pdPlusMinusPrice (_type, plusBtn, minusBtn, countInput, _id, price);

}

function cartOpPlusMinusInit (_type, plusBtn, minusBtn, pd_id, op_id, price) {
    let countInput = document.querySelector('[id="op-count-' + `${op_id}` + '"]');
    opPlusMinusPrice (_type, plusBtn, minusBtn, countInput, pd_id, op_id, price);

}

function pdPlusMinusPrice (_type, plusBtn, minusBtn, countInput, _id, price) {
    let objectNum = Number(countInput.value);
    let objectPrice = price;
    plusBtn.addEventListener("click", function (e){
        console.log(e.target)
        e.preventDefault();
        objectNum += 1;
        cartPdCountPriceApply(_type, objectNum, objectPrice, _id);
    }, false);

    minusBtn.addEventListener("click", function (e){
        e.preventDefault();
        objectNum -= 1;
        if (objectNum >= 1) {
            cartPdCountPriceApply(_type, objectNum, objectPrice, _id);
        } else {
            objectNum = 1;
        }
    }, false);
}

function cartPdCountPriceApply (_type, objectNum, objectPrice, pd_id) {
    if (_type === "product") {
        let countInput = document.querySelector('[id="pd-count-' + `${pd_id}` + '"]');
        const hiddenPdTotalPriceInput = document.querySelector('[id="pd-total-price-' + `${pd_id}` + '"]');
        const pdTotalPriceSpan = document.querySelector('[id="pd-total-price-span-' + `${pd_id}` + '"]');
        countInput.value = objectNum;
        hiddenPdTotalPriceInput.value = Number(objectNum * objectPrice);
        pdTotalPriceSpan.innerText = othersScript.intComma(objectNum * objectPrice);
        cartPdOpTotalPriceCalc(pd_id);
    }

}

function opPlusMinusPrice (_type, plusBtn, minusBtn, countInput, pd_id, op_id, price) {
    let objectNum = Number(countInput.value);
    let objectPrice = price;
    plusBtn.addEventListener("click", function (e){
        e.preventDefault();
        objectNum += 1;
        cartOpCountPriceApply(_type, objectNum, objectPrice, pd_id, op_id);
    }, false);

    minusBtn.addEventListener("click", function (e){
        e.preventDefault();
        objectNum -= 1;
        if (objectNum >= 1) {
            cartOpCountPriceApply(_type, objectNum, objectPrice, pd_id, op_id);
        } else {
            objectNum = 1;
        }
    }, false);
}

function cartOpCountPriceApply (_type, objectNum, objectPrice, pd_id, op_id) {
    if (_type === "option") {
        const countInput = document.querySelector('[id="op-count-' + `${op_id}` + '"]');
        const hiddenTotalPriceInput = document.querySelector('[id="op-total-price-' + `${op_id}` + '"]');
        const OpTotalPriceSpan = document.querySelector('[id="op-total-price-span-' + `${op_id}` + '"]');
        countInput.value = objectNum;
        hiddenTotalPriceInput.value = Number(objectNum * objectPrice);
        console.log("hiddenTotalPriceInput.value", hiddenTotalPriceInput.value)
        OpTotalPriceSpan.innerText = othersScript.intComma(objectNum * objectPrice);

        cartPdOpTotalPriceCalc(pd_id, op_id);

    }

}

function cartPdOpTotalPriceCalc (pd_id) {
    let totalPriceHiddenInput = document.querySelector('[id="total-price-' + `${pd_id}` + '"]');
    let totalPriceSpan = document.querySelector('[class="total-price-' + `${pd_id}` + '"]');
    const pdTotalPrice = document.querySelector('[id="pd-total-price-' + `${pd_id}` + '"]').value;
    const productMatchingOptionsAll = document.querySelectorAll('[data-insert-product-id="' + `${pd_id}` + '"]');
    console.log("Number(opTotalPriceCalc())", Number(cartOpTotalPriceCalc(productMatchingOptionsAll)))
    const pdOpTotalPrice = Number(pdTotalPrice) + Number(cartOpTotalPriceCalc(productMatchingOptionsAll));
    console.log("pdOpTotalPrice()", pdOpTotalPrice);
    totalPriceHiddenInput.value = pdOpTotalPrice;
    totalPriceSpan.innerHTML = othersScript.intComma(pdOpTotalPrice);
    return pdOpTotalPrice;
}

function cartOpTotalPriceCalc (matchingOptionsAll) {
    let opTotalPrice = 0;
    matchingOptionsAll.forEach(function (matchingOption){
        const optionId = matchingOption.getAttribute("data-option-id");
        const opLinePrice = matchingOption.querySelector(".op-total-price");
        let a = Number(opLinePrice.value);
        opTotalPrice += a;
    });

    return opTotalPrice;

}

function pointAllPriceInnerHtml(response) {
    couponPointPayPriceInnerHtml (response);
    const cartTotalPriceSpan = document.querySelector("#cart_total_price");
    cartTotalPriceSpan.innerHTML = othersScript.intComma(response.cart_total_price);
}

function couponPointPayPriceInnerHtml (response) {
    const prepPointSpan = document.querySelector("#prep-point");
    prepPointSpan.innerHTML = othersScript.intComma(response.prep_point);
    const newRemainedPointSpan = document.querySelector("#new-remained-point");
    newRemainedPointSpan.innerHTML = othersScript.intComma(response.new_remained_point);

    const realPayPriceInput = document.querySelector("#real-pay-price");
    realPayPriceInput.value = Number(response.get_total_price) + response.get_total_delivery_pay;
    const cartPayPriceSpan = document.querySelector("#cart_pay_price");
    cartPayPriceSpan.innerHTML = othersScript.intComma(Number(response.get_total_price) + response.get_total_delivery_pay);
}

function flashAlertDivInnerHtml (flashAlert_div, response) {
    if (response.flash_message) {
        flashAlert_div.style.display = "block";
        flashAlert_div.innerHTML = `<div class="flashes" uk-alert id="check-alert">
                                        <div class="alert alert-danger" role="alert">` + response.flash_message + `</div>
                                        <button class="uk-alert-close mt-5" type="button" uk-close></button></div>`;
    } else {
        flashAlert_div.innerHTML = `<div class="flashes" uk-alert id="check-alert">
                                        <div class="alert alert-danger" role="alert">사용 가능합니다.</div>
                                        <button class="uk-alert-close mt-5" type="button" uk-close></button></div>`;
    }
}

function flashAlertDivDisplayNone (flashAlert_div, closeBtn) {
    closeBtn.addEventListener("click", function (e) {
        flashAlert_div.style.display = "none";
    }, false);
}

function pointCouponFlashTagRemove(response){

    const pointLogTag = document.querySelector(".point-log");
    const usedPointCancelModal = document.querySelector('[id="usedpoint-cancel-modal-' + `${response.point_log_id}` + '"]');
    if (response.used_point === 0) {
        if (pointLogTag) {
            pointLogTag.remove();
            if (usedPointCancelModal) {
                usedPointCancelModal.remove();
            }

        }
    }

    const usedCouponLabel = document.querySelector(".usedcoupon-container.main-width .label");
    const eachUsedCouponAll = document.querySelectorAll(".each");
    const usedCouponCancelModalAll = document.querySelectorAll(".usedcoupon-cancel-modal");
    if (response.coupon_total === 0) {
        if (usedCouponLabel) {
            usedCouponLabel.remove();
        }
        if (eachUsedCouponAll.length > 0) {
            for (let i = 0; i < eachUsedCouponAll.length; i++) {
                eachUsedCouponAll[i].remove();
            }
        }
        if (usedCouponCancelModalAll.length > 0) {
            for (let i = 0; i < usedCouponCancelModalAll.length; i++) {
                usedCouponCancelModalAll[i].remove();
            }
        }
    }

    const flashAlert_div = document.querySelector(".coupon-point-alert");
    const flashes = flashAlert_div.querySelector(".flashes");
    if (flashAlert_div.style.display === "block") {
        flashAlert_div.style.display = "none";
        flashes.remove();
    }

}