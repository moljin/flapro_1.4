"use strict"
/*jshint esversion: 6 */

productOptionCountPriceInit();
function productOptionCountPriceInit () {
    try {
        // product count change
        const pdPlusBtn = document.querySelector(".pd-plus");
        const pdMinusBtn = document.querySelector(".pd-minus");
        const pd_type = "product";
        const productIdTag = document.querySelector("#pd-count");
        const pd_id = productIdTag.getAttribute("data-pd-id");
        const pd_price = document.querySelector("#pd-applied-price").value;
        plusMinusInit(pd_type, pdPlusBtn, pdMinusBtn, pd_id, pd_price);

        // option select count change
        const optionSelect = document.querySelector(".uk-select");
        const selectContainer = document.querySelector(".select-container");
        optionSelect.addEventListener("change", function (e) {
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
                    // contentType: false, processData: false, 는 필수로 있어야 된다.

                    success: function (response) {
                        if (response.error) {
                            AjaxUtils.responseErrorAlert(request, response);
                        } else {
                            if (response._id && response._title && response._price) {
                                insertSelectOption(optionSelect, selectContainer, response._id, response._title, response._price);
                                const opPlusBtn = document.querySelector('[data-plus-id="op-plus-' + `${response._id}` + '"]');
                                const opMinusBtn = document.querySelector('[data-minus-id="op-minus-' + `${response._id}` + '"]');
                                const _type = "option";
                                pdOpTotalPriceCalc();
                                plusMinusInit(_type, opPlusBtn, opMinusBtn, response._id, response._price);
                            }
                            if (response._data_r) {
                                console.log("data_r", response._data_r)
                            }
                        }
                    },
                    error: function (err) {
                        AjaxUtils.serverErrorAlert(err);
                    }
                });
            }
        });

        // option select cancel change
        document.addEventListener("click", function (e) {
            let target = e.target;
            if (target.classList.contains("op-cancel")) {
                let _id = target.getAttribute("data-cancel-id");
                let postCancelTotalPrice = pdOpTotalPriceCalc() - Number(cancelOpTotalPrice(_id));
                let totalPriceHiddenInput = document.querySelector("#total-price");
                let totalPriceSpan = document.querySelector(".total-price");
                totalPriceHiddenInput.value = postCancelTotalPrice;
                totalPriceSpan.innerHTML = othersScript.intComma(postCancelTotalPrice);
            }
        }, false);
    } catch (e) {
        // console.log(e);
    }

}

function insertSelectOption (selectTag, div, _id, title, price) {
    let oldInsertDiv = document.querySelector('[data-id="op-' + `${_id}` + '"]');
    if (oldInsertDiv) {
        alert("이미 선택한 옵션이에요!");
        selectTag.value = "none";
    }
    else {
        let newDiv = `<div class="op-select-insert" uk-alert>
                          <div class="op-title mb-10" data-id="op-${_id}">${title} / ${othersScript.intComma(Number(price))}원</div>
                            <button class="op-cancel uk-alert-close" data-cancel-id="${_id}" uk-close>취소</button>
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
        div.insertAdjacentHTML('afterend', newDiv);
        selectTag.value = "none";

    }

}

function plusMinusInit (_type, plusBtn, minusBtn, _id, price) {
    let objectNum = 1;
    let objectPrice = price;
    plusBtn.addEventListener("click", function (e){
        e.preventDefault();
        objectNum += 1;
        countPriceApply(_type, objectNum, objectPrice, _id);
    }, false);

    minusBtn.addEventListener("click", function (e){
        e.preventDefault();
        objectNum -= 1;
        if (objectNum >= 1) {
            countPriceApply(_type, objectNum, objectPrice, _id);
        } else {
            objectNum = 1;
        }
    }, false);

}

function countPriceApply (_type, objectNum, objectPrice, _id) {
    if (_type === "product") {
        const countInput = document.querySelector("#pd-count");
        const hiddenPdTotalPriceInput = document.querySelector("#pd-total-price");
        const pdTotalPriceSpan = document.querySelector("#pd-total-price-span");
        countInput.value = objectNum;
        hiddenPdTotalPriceInput.value = Number(objectNum * objectPrice);
        pdTotalPriceSpan.innerText = othersScript.intComma(objectNum * objectPrice);
        // countInput.value 와 hiddenTotalPriceInput.value 를 이용해 총합계 금액을 계산하고, 이것과 계산총합을 ajax 로 보낸다.
        pdOpTotalPriceCalc();
    }
    if (_type === "option") {
        const countInput = document.querySelector('[id="op-count-' + `${_id}` + '"]');
        const hiddenTotalPriceInput = document.querySelector('[id="op-total-price-' + `${_id}` + '"]');
        const OpTotalPriceSpan = document.querySelector('[id="op-total-price-span-' + `${_id}` + '"]');
        countInput.value = objectNum;
        hiddenTotalPriceInput.value = Number(objectNum * objectPrice);
        OpTotalPriceSpan.innerText = othersScript.intComma(objectNum * objectPrice);
        // countInput.value 와 hiddenTotalPriceInput.value 를 이용해 총합계 금액을 계산하고, 이것과 계산총합을 ajax 로 보낸다.

        pdOpTotalPriceCalc();

    }

}

function opTotalPriceCalc () {
    let opTotalPrice = 0;
    const selectOpInputAll = document.querySelectorAll(".op-total-price");
    selectOpInputAll.forEach(function (opInput) {
        let a = Number(opInput.value);
        opTotalPrice += a;
    });
    return opTotalPrice;

}

function pdOpTotalPriceCalc () {
    let totalPriceHiddenInput = document.querySelector("#total-price");
    let totalPriceSpan = document.querySelector(".total-price");
    const pdTotalPrice = document.querySelector("#pd-total-price").value;
    const pdOpTotalPrice = Number(pdTotalPrice) + Number(opTotalPriceCalc());
    totalPriceHiddenInput.value = pdOpTotalPrice;
    totalPriceSpan.innerHTML = othersScript.intComma(pdOpTotalPrice);
    return pdOpTotalPrice;
}

function cancelOpTotalPrice(_id) {
    let opTotalPrice = document.querySelector('[id="op-total-price-' + `${_id}` + '"]');
    return Number(opTotalPrice.value);
}
