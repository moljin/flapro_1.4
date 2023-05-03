 "use strict"
 /*jshint esversion: 6 */

document.addEventListener('DOMContentLoaded', function () {
    const contentContainer = document.querySelector(".content-container");
    const textAddBtn = document.querySelector(".text-add-btn");

    let cancelBtn = document.getElementsByClassName("cancel");
    let cancelImageBtn = document.getElementsByClassName("cancel-input-btn");

    let textAreaDiv = document.getElementsByClassName("text-area");
    let cancelTextBtn = document.getElementsByClassName("cancel-text-btn");

    const maxInputFields = 11;

    const textDiv = `<p class="text-area" data-placeholder="내용을 입력하세요." contenteditable="true"></p>`;
    const lastAlert = `<div class="option-form" uk-alert>
                            <a class="uk-alert-close" uk-close></a>           
                            <div class="mt-10">더이상 추가 할수 없습니다.
                                <div class="mt-5">저장 혹은 새로고침후 다시 시작해주세요!</div>
                                <div class="mt-5">(단, 최종적으로 등록할 수 있는 이미지수에는 제한이 없습니다.)</div>
                            </div>                        
                        </div>`;

    let addInputCount = 1;

    textAddBtn.addEventListener("click", function (e){
        if (((e.target === textAddBtn) || (e.target.parentElement === textAddBtn)) && (addInputCount < maxInputFields)) {
            addInputCount++;
            contentContainer.insertAdjacentHTML("beforeend", textDiv);
            contentContainer.style.height = "unset";

            if (addInputCount === 11) {
                    contentContainer.insertAdjacentHTML('beforeend', textDiv);
                }

            for (let i = 0; i < textAreaDiv.length; i++) {
                textAreaDiv[i].setAttribute("id", "text-" +(i));

                // cancelTextBtn[i].id = "cancel-text-btn-" +(i);
            }

        }
    }, false);

});