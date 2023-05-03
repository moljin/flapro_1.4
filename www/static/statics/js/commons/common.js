"use strict"
/*jshint esversion: 6 */

let ImageUtils;
let AjaxUtils;
let AlertUtils;
let SunEditorUtils;
let othersScript;

let module2Utils;

(function(window){
    let useInRelatedImage = {
        eachImagePreview: function (_width, _height, imgInput, previewTag, existingImgPath, existingDeleteBtn, clickDiv) {
            imgInput.addEventListener("change", function (e) {
                e.preventDefault();
                previewTag.style.cssText = ` width:` + _width + `;
                                height:` + _height + `;
                                object-fit:cover;
                                `;

                // Ajax 로 multiple image save(sunimage 방식으로) 할때 필요
                previewTag.setAttribute("data-file-name", imgInput.value.split('fakepath\\')[1]);

                let imgInputFile = imgInput.files[0];
                let reader = new FileReader();
                reader.addEventListener("load", function () {
                    previewTag.src = reader.result;

                    // flash div 의 alert 지우기 (flask flash and ajax flash_message)
                    const alertInnerElement = document.querySelector('div.flashes');
                    if (alertInnerElement) {
                        // if 분기는 shop cover_image 모달 수정에서, ajax flash_message alert 부모 요소 display none
                        if (alertInnerElement.parentElement.classList.contains("modal-alert")) {
                            alertInnerElement.parentElement.style.display = "none";
                        }
                        alertInnerElement.remove();
                    }
                    // shop cover_image 모달 수정에서, 삭제를 선택했다가 confirm 하지 않고, 다른 이미지를 업로드하려할때
                    const existingDeleteBtnList = document.querySelectorAll(".existing-btn");
                    if (existingDeleteBtnList) {
                        existingDeleteBtnList.forEach(function (deleteBtn, idx){
                            if (deleteBtn.style.display === "none") {
                                deleteBtn.style.display = "block";
                            }
                        });
                    }
                    if (existingDeleteBtn) { // 업로드하는 이미지와 짝인 existingDeleteBtn
                        existingDeleteBtn.style.display = "none"; // 이미 none 인 경우도 있겠지만... 위 로직에서 돌면서 block 으로 만들었겠지...
                        existingDeleteBtn.innerHTML = "";
                        existingDeleteBtn.classList.remove("existing-cover");
                        existingDeleteBtn.classList.add("none");
                    }

                    const existingImageIdTags = document.querySelectorAll('[name="image_id"]');
                    if (existingImageIdTags) {
                        existingImageIdTags.forEach(function (existingImageIdTag, idx){
                            console.log("existingImageIdTag;");
                            // existingImageIdTag.value = "";
                        });
                    }


                }, false);

                if (imgInputFile) {
                    reader.readAsDataURL(imgInputFile);
                } else {
                    previewTag.src = existingImgPath; // 원래 이미지로...

                    if (previewTag.style.display === "none") {
                        previewTag.style.display = "block";
                    } else {
                        if (existingDeleteBtn) { // 업로드하는 이미지와 짝인 existingDeleteBtn
                            existingDeleteBtn.style.display = "block";
                            existingDeleteBtn.innerHTML = "삭제";
                            existingDeleteBtn.classList.add("existing-cover");
                            existingDeleteBtn.classList.remove("none");
                        }
                    }
                }
            }, false);
        },
        imageSizeCheck: function (imgInput) {
            imgInput.addEventListener("change", function (e) {
                e.preventDefault();
                let img = new Image();
                let imgInputFile = imgInput.files[0];
                let fileSize = imgInputFile.size;
                let maxSize = 5 * 1024 * 1024; //5MB
                let _URL = window.URL || window.webkitURL;
                img.src = _URL.createObjectURL(imgInputFile);

                console.log(imgInputFile.name);

                img.onload = function () {
                    if (fileSize <= maxSize) {
                        console.log("5MB 초과 하지 않음");
                    } else {
                        console.log("5MB 초과");
                        alert("이미지 용량이 5MB를 초과했어요!");
                        imgInput.value = "";
                        return false;
                    }

                };
            }, false);
        },

    };

    let useInAjax = {
        tokenCreate: function (email, add_if, alertDiv) {
            let formData = new FormData();
            formData.append("email", email);
            formData.append("add_if", add_if);
            let url = tokenCreateAjax;
            let type = "onlyFlashMessageOrWindowReload";
            AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, alertDiv, type, null);
        },
        flashMessageRedirectRemoveDiv: function (_url, formData, alertDiv, _type, removeDiv) {
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
                        if (_type === "onlyFlashMessageOrWindowReload") {
                            if (response.flash_message) {
                                AlertUtils.alertDisplay(alertDiv, response.flash_message);
                            }
                            if (response._success) {
                                window.location.reload();
                            }
                            if (response._err && response.res_msg) {
                                window.location.href = response.redirect_url + '?res_msg=' + response.res_msg;
                            }
                        }
                        if (_type === "flashMessageRemoveDiv") {
                            if (response.flash_message && removeDiv) {
                                AlertUtils.alertDisplay(alertDiv, response.flash_message);
                                removeDiv.remove();
                            }
                        }
                        if (_type === "successRedirect") {
                            /*location.href vs location.assign vs location.replace 차이점 https://im-developer.tistory.com/219*/
                            if (response._success && response._delete) {
                                window.location.href = response.redirect_url;
                            } else if (response._success && response.flash_message) {
                                AlertUtils.alertDisplay(alertDiv, response.flash_message);
                                window.location.assign(response.redirect_url);
                                window.location.reload();
                            } else if (response._success) { /*자신의 페이지를 강제로 한번더 reload*/
                                window.location.assign(response.redirect_url);
                                // alert(response.flash_message); // dropzone delete에서 여러장인경우 거슬림
                                window.location.reload(); // window.location.reload(true); //true 가 없어도 된다.
                            } else if (response._err && response.res_msg) {
                                window.location.href = response.redirect_url + '?res_msg=' + response.res_msg;
                            }
                        }
                        if (_type === "requestGetParam") {
                            if (response.flash_message) {
                                AlertUtils.alertDisplay(alertDiv, response.flash_message);
                            }
                            if (response._success && response.res_msg) {
                                AlertUtils.alertRemove(alertDiv);
                                window.location.href = response.redirect_url + '?res_msg=' + response.res_msg;
                                // success_msg를 request.args.get으로 def login(): 에서 받아서 flash(success_msg)로 사용한다.
                            } else if (response._success && response.comment_id) {
                                window.location.assign(response.redirect_url + '#comment_' + response.comment_id);
                                window.location.reload();
                            } else if (response._err && response.res_msg) {
                                window.location.href = response.redirect_url + '?res_msg=' + response.res_msg;
                            }
                        }

                    }
                },
                error: function (err) {
                    console.log("여긴가")
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        },
        flashMessageFlashHTML: function (_url, formData, alertDiv, _type, extraFirstElement, extraSecondElement, extraThirdElement) {
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
                        if (_type === "flashMessageFlashHTML") {
                            if (response.flash_message) {
                                AlertUtils.alertDisplay(alertDiv, response.flash_message);
                                // if (response.flash_message === "수정된 내용이 없습니다.") {
                                //     extraSecondElement.style.display = "none";
                                //     extraThirdElement.style.display = "block";
                                // }

                            }
                            if (response._obj === "product_category") {
                                if (response.o_save) {
                                    if (response.available_display === true) {
                                        extraFirstElement.innerHTML = `<div class="title">${response._title}</div>
                                                                <div class="available">노출여부: 
                                                                    <input disabled checked class="uk-checkbox ml-10" name="available_display" type="checkbox">
                                                                </div>`;
                                    } else {
                                        extraFirstElement.innerHTML = `<div class="title">${response._title}</div>
                                                                <div class="available">노출여부: 
                                                                    <input disabled class="uk-checkbox ml-10" name="available_display" type="checkbox">
                                                                </div>`;
                                    }

                                }
                                if (response._check === "change_check") {
                                    console.log("change_check", response._check)
                                    if (response.available_display === true) {
                                        extraFirstElement.innerHTML = `<div class="mt-10">
                                                                    <input class="uk-input title" maxlength="200" minlength="1" name="title" placeholder="상품 카테고리 이름" required="required" type="text" value="${response._title}">
                                                                </div>
                                                                <div class="mt-10 mb-10">노출여부: 
                                                                    <input checked="checked" class="available_display uk-checkbox ml-10" name="available_display" type="checkbox">
                                                                </div>`;
                                    } else {
                                        extraFirstElement.innerHTML = `<div class="mt-10">
                                                                    <input class="uk-input title" maxlength="200" minlength="1" name="title" placeholder="상품 카테고리 이름" required="required" type="text" value="${response._title}">
                                                                </div>
                                                                <div class="mt-10 mb-10">노출여부: 
                                                                    <input class="available_display uk-checkbox ml-10" name="available_display" type="checkbox">
                                                                </div>`;
                                    }
                                }
                                if (response._check === "delete_check") {
                                    let deleteHtml = `<div class="response-container">
                                                        "${response.category_title}"(을)를 정말로 삭제하시겠습니까?
                                                        <input type="hidden" id="user_id_`+response.user_id+`" name="user_id" value="`+response.user_id+`">
                                                        <input type="hidden" id="shop_id_`+response.shop_id+`" name="shop_id" value="`+response.shop_id+`">
                                                        <input type="hidden" id="category_id_`+response.category_id+`" name="category_id" value="`+response.category_id+`">
                                                        <div class="btn mt-5"><button class="delete-confirm-btn uk-button uk-button-default" type="button" uk-tooltip="title: 삭제; pos: bottom"><i class="fas fa-trash-alt"></i></button></div>
                                                        </div>`;
                                    AlertUtils.alertDisplay(alertDiv, deleteHtml);

                                    let alertCloseBtn = alertDiv.querySelector(".uk-alert-close");
                                    alertCloseBtn.addEventListener("click", function (e){
                                        e.preventDefault();
                                        extraSecondElement.style.display = "block";
                                    },false);

                                    let deleteConfirmBtn = alertDiv.querySelector(".delete-confirm-btn");
                                    deleteConfirmBtn.addEventListener("click", function (e){
                                        e.preventDefault();
                                        let _url = productCategoryDeleteAjax;
                                        let userId = document.querySelector("#user_id").value;
                                        let shopId = document.querySelector("#shop_id").value;
                                        let _type = "onlyFlashMessageOrWindowReload";
                                        extraThirdElement.remove();
                                        let formData = new FormData();
                                        formData.append('user_id', response.user_id);
                                        formData.append("shop_id", response.shop_id);
                                        formData.append("category_id", response.category_id);
                                        AjaxUtils.flashMessageRedirectRemoveDiv(_url, formData, alertDiv, _type, null);
                                    },false);

                                }
                            }

                        }

                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        },

        subscribeRequest: function (_url, formData, alertDiv, _type, objId) {
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
                        if (response.checked_message) {
                            AlertUtils.alertDisplay(alertDiv, response.checked_message);
                        } else if (response.admin_success === "admin success") {
                            window.location.reload();
                        } else {
                            AlertUtils.alertRemove(alertDiv);
                            AlertUtils.alertDisplay(alertDiv, response.flash_message);
                            document.querySelector("#subscribe-btn").style.display = "none";
                            document.querySelector("#cancel-btn").style.display = "block";
                            const subscribeContainer = document.querySelector(".viewcount-subscribe-container .subscribe-container");

                            let count = response.subscribe_count + 2653;
                            let countSpan = document.querySelector(".viewcount-subscribe-container span.subscribe-count");
                            countSpan.innerHTML = `구독: ` + count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') + `명`;

                            const cancel_modal = `<div id="subscribe-cancel-modal" class="uk-flex-top" uk-modal>
                                                        <div class="uk-modal-dialog uk-modal-body uk-margin-auto-vertical">
                                                            <button class="uk-modal-close-default" type="button" uk-close></button>
                                                            정말로 구독을 취소하시겠어요?
                                                            <div class="subscribe-cancel-btn uk-align-right uk-inline">
                                                                <button id="subscribe-cancel-btn" class="uk-button uk-button-primary mt-40 uk-modal-close" type="button">구독 취소</button>
                                                            </div>
                                                        </div>
                                                    </div>`;
                            subscribeContainer.insertAdjacentHTML("beforeend", cancel_modal);
                            const shopSubscribeCancelBtn = document.querySelector("#subscribe-cancel-btn");
                            shopSubscribeCancelBtn.addEventListener('click', function (e) {
                                e.preventDefault();
                                if (_type === "shop") {
                                    AjaxUtils.shopSubscribeCancelFunc(objId, null);
                                } else if (_type === "ac") {
                                    AjaxUtils.acSubscribeCancelFunc(objId, null);
                                }

                            }, false);
                        }

                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        },
        subscribeCancelRequest: function (_url, formData, flashAlert_div) {
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
                        if (response.no_auth_message) {
                            AlertUtils.alertDisplay(flashAlert_div, response.no_auth_message);
                        }
                        if (response.admin_success === "admin success") {
                            window.location.reload();
                        } else {
                            AlertUtils.alertRemove(flashAlert_div);
                            AlertUtils.alertDisplay(flashAlert_div, response.flash_message);
                            document.querySelector("#subscribe-btn").style.display = "block";
                            document.querySelector("#cancel-btn").style.display = "none";
                            const subscribeCancelModal = document.querySelector("#subscribe-cancel-modal");

                            let count = response.subscribe_count + 2653;
                            let countSpan = document.querySelector(".viewcount-subscribe-container span.subscribe-count");
                            countSpan.innerHTML = `구독: ` + count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') + `명`;
                            subscribeCancelModal.remove();
                        }

                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        },
        shopSubscribeCancelFunc: function (shop_id, user_id) {
            const flashAlert_div = document.querySelector(".shop-alert");
            let _url = shopSubscribeCancelAjax;
            let formData = new FormData();
            formData.append("shop_id", shop_id);
            if (user_id) { // 어드민단
                formData.append("user_id", user_id);
            }
            AjaxUtils.subscribeCancelRequest(_url, formData, flashAlert_div);
        },
        acSubscribeCancelFunc: function (category_id, user_id) {
            const flashAlert_div = document.querySelector(".subscribe-alert");
            let _url = acSubscribeCancelAjax;
            let formData = new FormData();
            formData.append("category_id", category_id);
            if (user_id) { // 어드민단
                formData.append("user_id", user_id);
            }
            AjaxUtils.subscribeCancelRequest(_url, formData, flashAlert_div);
        },

        voteRequest: function (_url, formData, alertDiv, _type, objId) {
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
                        if (response.checked_message) {
                            AlertUtils.alertDisplay(alertDiv, response.checked_message);
                        } else if (response.admin_success === "admin success") {
                            window.location.reload();
                        } else {
                            AlertUtils.alertRemove(alertDiv);
                            AlertUtils.alertDisplay(alertDiv, response.flash_message);
                            document.querySelector("#vote-btn").style.display = "none";
                            document.querySelector("#cancel-btn").style.display = "block";
                            const voteContainer = document.querySelector(".viewcount-vote-container .vote-container");

                            let count = response.vote_count + 2653;
                            let countSpan = document.querySelector(".viewcount-vote-container span.vote-count");
                            // countSpan.innerHTML = `추천: ` + count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') + `명`;
                            countSpan.innerHTML = count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
                            const cancel_modal = `<div id="vote-cancel-modal" class="uk-flex-top" uk-modal>
                                                        <div class="uk-modal-dialog uk-modal-body uk-margin-auto-vertical">
                                                            <button class="uk-modal-close-default" type="button" uk-close></button>
                                                            정말로 추천을 취소하시겠어요?
                                                            <div class="vote-cancel-btn uk-align-right uk-inline">
                                                                <button id="vote-cancel-btn" class="uk-button uk-button-primary mt-40 uk-modal-close" type="button">추천 취소</button>
                                                            </div>
                                                        </div>
                                                    </div>`;
                            voteContainer.insertAdjacentHTML("beforeend", cancel_modal);
                            const voteCancelBtn = document.querySelector("#vote-cancel-btn");
                            voteCancelBtn.addEventListener('click', function (e) {
                                e.preventDefault();
                                if (_type === "article") {
                                    AjaxUtils.articleVoteCancelFunc(objId, null);
                                } else if (_type === "product") {
                                    AjaxUtils.productVoteCancelFunc(objId, null);
                                }


                            }, false);

                        }

                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        },
        voteCancelRequest: function (_url, formData, alertDiv) {
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
                        if (response.no_auth_message) {
                            AlertUtils.alertDisplay(alertDiv, response.no_auth_message);
                        }
                        if (response.admin_success === "admin success") {
                            window.location.reload();
                        } else {
                            AlertUtils.alertRemove(alertDiv);
                            AlertUtils.alertDisplay(alertDiv, response.flash_message);
                            document.querySelector("#vote-btn").style.display = "block";
                            document.querySelector("#cancel-btn").style.display = "none";
                            const voteCancelModal = document.querySelector("#vote-cancel-modal");

                            let count = response.vote_count + 2653;
                            let countSpan = document.querySelector(".viewcount-vote-container span.vote-count");
                            // countSpan.innerHTML = `추천: ` + count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') + `명`;
                            countSpan.innerHTML = count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
                            voteCancelModal.remove();
                        }
                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        },
        productVoteCancelFunc: function (product_id, user_id) {
            const flashAlert_div = document.querySelector(".vote-alert");
            let _url = productVoteCancelAjax;
            let formData = new FormData();
            formData.append("product_id", product_id);
            if (user_id) { // 어드민단
                formData.append("user_id", user_id);
            }
            AjaxUtils.voteCancelRequest(_url, formData, flashAlert_div);
        },
        articleVoteCancelFunc: function (article_id, user_id) {
            const flashAlert_div = document.querySelector(".vote-alert");
            let _url = articleVoteCancelAjax;
            let formData = new FormData();
            formData.append("article_id", article_id);
            if (user_id) { // 어드민단
                formData.append("user_id", user_id);
            }
            AjaxUtils.voteCancelRequest(_url, formData, flashAlert_div);
        },

        hashTagSearch: function (url, hashTag) {
            let request = $.ajax({
                url: url,
                type: 'GET',
                data: {hash_tag: hashTag},
                dataType: 'json',

                success: function (response) {
                    if (response.error) {
                        AjaxUtils.responseErrorAlert(request, response);
                    } else {
                        console.log("response.hash_tag", response._hash_tag);
                        window.location.href = response.redirect_url + '?_id=' + response._id + '&res_tag=' + response._hash_tag;
                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        },
        responseErrorAlert: function (request, response) {
            alert("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + response.error);
        },
        serverErrorAlert: function (err) {
            console.log(err);
            alert('내부 오류가 발생하였습니다.\n 확인후 다시 시도해주세요.');
            window.location.reload();
        },

    };

    let useInFlashAlert = {
        alertDisplay: function (alertDiv, message) {
            if (alertDiv) {
                alertDiv.style.display = "block";
                alertDiv.innerHTML = `<div class="flashes" uk-alert>  <!--id="check-alert"-->
                                        <div class="alert alert-danger" role="alert">` + message + `</div>
                                        <button class="uk-alert-close mt-5" type="button" uk-close></button></div>`;
            }
        },
        alertRemove: function (alertDiv) {
            if (alertDiv) {
                const alertInnerElement = alertDiv.querySelector('div.flashes');
                if (alertInnerElement) {
                    alertDiv.style.display = "none";
                    alertInnerElement.remove();
                }
            }
        }
    };

    let useInSunEditor = {
        sunHelpPlugIn: function () {
            return {
                name: 'help',
                display: ('command'),
                title: '도움말',
                innerHTML: '<span uk-icon="question"></span>',
                buttonClass: 'help-command',
                add: function (core, targetElement) {
                    const context = core.context;
                    context.help = {
                        targetButton: targetElement,
                    };
                },
            };
        },
        customPlugIn: function () {
            let helpPlugIn = SunEditorUtils.sunHelpPlugIn();
            return {
                plugins: [helpPlugIn],
            };
        },
        baseSetting: function () {
            return {
                display: 'block',
                width: '100%',
                //height: 'auto',
                minHeight: 300,
                popupDisplay: 'full',
                charCounter: true,
                charCounterLabel: '글자수 :',
                font: ['Arial', 'Times New Roamn', 'NotoSansKR', 'Comic Sans MS', 'Courier New', 'Impact', 'Georgia', 'tahoma', 'Trebuchet MS', 'Verdana', '맑은 고딕', '굴림', '돋움', '바탕', '궁서'],
                defaultStyle: "font-family: sans-serif; font-size: 16px;", /*font 기본값 설정*/
                lang: SUNEDITOR_LANG['ko'],
                placeholder: '',
                imageGalleryUrl: 'https://etyswjpn79.execute-api.ap-northeast-1.amazonaws.com/suneditor-demo',

                templates: [
                    {
                        name: 'Template-1',
                        html: '<p>HTML source1</p>'
                    },
                    {
                        name: 'Template-2',
                        html: '<p>HTML source2</p>'
                    }
                ],
                codeMirror: CodeMirror,
                katex: katex,
            };
        },
        simpleButtons: function () {
            return {
                buttonList: [
                    ['undo', 'redo'],
                    ['fontSize'],
                    ['bold', 'underline', 'italic'],
                    ['strike', 'subscript', 'superscript'],
                    ['align', 'link'],
                    ['removeFormat', 'codeView'],

                    ['%600', [
                        ['undo', 'redo'],
                        ['fontSize'],
                        ['bold', 'underline', 'italic', 'align'],
                        ['-right', ':r-More Rich-default.more_plus', 'strike', 'subscript', 'superscript', 'link', 'removeFormat', 'codeView'],
                    ]],

                    ['%430', [
                        ['undo', 'redo'],
                        ['fontSize'],
                        ['-right', ':r-More Rich-default.more_plus', 'strike', 'subscript', 'superscript', 'link', 'removeFormat', 'codeView'],
                        ['-right', ':i-More Misc-default.more_vertical', 'bold', 'underline', 'italic', 'align'],
                    ]],

                ],
            };
        },
        commentButtons: function () {
            return {
                buttonList: [
                    ['undo', 'redo'],
                    ['fontSize', 'formatBlock'],
                    ['bold', 'link'],
                    ['-right', 'image', 'video', 'showBlocks', 'codeView', 'help'],

                    ['%560', [
                        [':t-More Text-default.more_text', 'undo', 'redo', 'fontSize', 'formatBlock'],
                        ['bold', 'link'],
                        ['-right', ':r-More Rich-default.more_plus', 'image', 'video', 'showBlocks', 'codeView', 'help'],
                    ]]

                ],
            };
        },
        generalButtons: function () {
            return {
                buttonList: [
                    /*default*/
                    ['undo', 'redo'],
                    ['font', 'fontSize', 'formatBlock'],
                    ['paragraphStyle', 'blockquote'],
                    ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                    ['fontColor', 'hiliteColor', 'textStyle'],
                    ['removeFormat'],
                    ['outdent', 'indent'],
                    ['align', 'horizontalRule', 'list', 'lineHeight'],
                    ['table', 'link', 'image', 'video', 'math', 'showBlocks', 'codeView', 'help'],
                    ['%1546', [
                        ['undo', 'redo'],
                        ['font', 'fontSize', 'formatBlock'],
                        ['paragraphStyle', 'blockquote'],
                        ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                        ['fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['table', 'link', 'image', 'video', 'math', 'showBlocks', 'codeView', 'help'],
                    ]],
                    /*(min-width: 1455)*/
                    ['%1455', [
                        ['undo', 'redo'],
                        ['font', 'fontSize', 'formatBlock'],
                        ['paragraphStyle', 'blockquote'],
                        ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                        ['fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['table', 'link', 'image', 'video', 'math', 'showBlocks', 'codeView', 'help'],
                    ]],
                    /*(min-width: 1326)*/
                    ['%1326', [
                        ['undo', 'redo'],
                        ['font', 'fontSize', 'formatBlock'],
                        ['paragraphStyle', 'blockquote'],
                        ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                        ['fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['link', 'image', 'video'],
                        ['-right', ':r-More Rich-default.more_plus', 'table', 'math', 'showBlocks', 'codeView', 'help']
                    ]],
                    ['%1175', [
                        ['undo', 'redo'],
                        ['fontSize', 'formatBlock'],
                        [':p-More Paragraph-default.more_paragraph', 'font', 'paragraphStyle', 'blockquote'],
                        ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                        ['fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['link', 'image', 'video'],
                        ['-right', ':r-More Rich-default.more_plus', 'table', 'math', 'showBlocks', 'codeView', 'help']
                    ]],
                    /*(min-width: 817)*/
                    ['%1037', [
                        ['undo', 'redo'],
                        [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock', 'paragraphStyle', 'blockquote'],
                        ['bold', 'underline', 'italic', 'strike'],
                        ['subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['-right', ':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'math', 'showBlocks', 'codeView', 'help']
                    ]],
                    /*(min-width: 673)*/
                    ['%840', [
                        ['undo', 'redo'],
                        [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock', 'paragraphStyle', 'blockquote'],
                        [':t-More Text-default.more_text', 'subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle'],
                        ['bold', 'underline', 'italic', 'strike'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['-right', ':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'math', 'showBlocks', 'codeView', 'help']
                    ]],
                    /*(min-width: 525)*/
                    ['%690', [
                        ['undo', 'redo'],
                        [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock', 'paragraphStyle', 'blockquote'],
                        [':t-More Text-default.more_text', 'bold', 'underline', 'italic', 'strike', 'subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['-right', ':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'math', 'showBlocks', 'codeView', 'help']
                    ]],
                    /*(min-width: 420)*/
                    ['%530', [
                        ['undo', 'redo'],
                        [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock', 'paragraphStyle', 'blockquote'],
                        [':t-More Text-default.more_text', 'bold', 'underline', 'italic', 'strike', 'subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle'],
                        [':e-More Line-default.more_horizontal', 'removeFormat', 'outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['-right', ':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'math', 'showBlocks', 'codeView', 'help'],
                    ]],
                    ['%440', [
                        ['undo', 'redo'],
                        [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock', 'paragraphStyle', 'blockquote'],
                        [':t-More Text-default.more_text', 'bold', 'underline', 'italic', 'strike', 'subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle'],
                        [':e-More Line-default.more_horizontal', 'removeFormat', 'outdent', 'indent'],
                        ['-right', ':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'math', 'showBlocks', 'codeView', 'help'],
                        ['-right', ':i-More Misc-default.more_vertical', 'align', 'horizontalRule', 'list', 'lineHeight']
                    ]]
                ],
            };
        },
        fullButtons: function () {
            return {
                buttonList: [
                    // default
                    ['undo', 'redo'],
                    ['font', 'fontSize', 'formatBlock'],
                    ['paragraphStyle', 'blockquote'],
                    ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                    ['fontColor', 'hiliteColor', 'textStyle'],
                    ['removeFormat'],
                    ['outdent', 'indent'],
                    ['align', 'horizontalRule', 'list', 'lineHeight'],
                    ['table', 'link', 'image', 'video', 'audio', 'math'],
                    ['imageGallery'],
                    ['fullScreen', 'showBlocks', 'codeView'],
                    ['preview', 'print'],
                    ['save', 'template'],
                    // (min-width: 1546)
                    ['%1546', [
                        ['undo', 'redo'],
                        ['font', 'fontSize', 'formatBlock'],
                        ['paragraphStyle', 'blockquote'],
                        ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                        ['fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['table', 'link', 'image', 'video', 'audio', 'math'],
                        ['imageGallery'],
                        ['fullScreen', 'showBlocks', 'codeView'],
                        ['-right', ':i-More Misc-default.more_vertical', 'preview', 'print', 'save', 'template']
                    ]],
                    // (min-width: 1455)
                    ['%1455', [
                        ['undo', 'redo'],
                        ['font', 'fontSize', 'formatBlock'],
                        ['paragraphStyle', 'blockquote'],
                        ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                        ['fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['table', 'link', 'image', 'video', 'audio', 'math'],
                        ['imageGallery'],
                        ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template']
                    ]],
                    // (min-width: 1326)
                    ['%1326', [
                        ['undo', 'redo'],
                        ['font', 'fontSize', 'formatBlock'],
                        ['paragraphStyle', 'blockquote'],
                        ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                        ['fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template'],
                        ['-right', ':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'audio', 'math', 'imageGallery']
                    ]],
                    // (min-width: 1123)
                    ['%1123', [
                        ['undo', 'redo'],
                        [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock', 'paragraphStyle', 'blockquote'],
                        ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                        ['fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template'],
                        ['-right', ':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'audio', 'math', 'imageGallery']
                    ]],
                    // (min-width: 817)
                    ['%817', [
                        ['undo', 'redo'],
                        [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock', 'paragraphStyle', 'blockquote'],
                        ['bold', 'underline', 'italic', 'strike'],
                        [':t-More Text-default.more_text', 'subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template'],
                        ['-right', ':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'audio', 'math', 'imageGallery']
                    ]],
                    // (min-width: 673)
                    ['%673', [
                        ['undo', 'redo'],
                        [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock', 'paragraphStyle', 'blockquote'],
                        [':t-More Text-default.more_text', 'bold', 'underline', 'italic', 'strike', 'subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        ['align', 'horizontalRule', 'list', 'lineHeight'],
                        [':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'audio', 'math', 'imageGallery'],
                        ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template']
                    ]],
                    // (min-width: 525)
                    ['%525', [
                        ['undo', 'redo'],
                        [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock', 'paragraphStyle', 'blockquote'],
                        [':t-More Text-default.more_text', 'bold', 'underline', 'italic', 'strike', 'subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle'],
                        ['removeFormat'],
                        ['outdent', 'indent'],
                        [':e-More Line-default.more_horizontal', 'align', 'horizontalRule', 'list', 'lineHeight'],
                        [':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'audio', 'math', 'imageGallery'],
                        ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template']
                    ]],
                    // (min-width: 420)
                    ['%420', [
                        ['undo', 'redo'],
                        [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock', 'paragraphStyle', 'blockquote'],
                        [':t-More Text-default.more_text', 'bold', 'underline', 'italic', 'strike', 'subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle', 'removeFormat'],
                        [':e-More Line-default.more_horizontal', 'outdent', 'indent', 'align', 'horizontalRule', 'list', 'lineHeight'],
                        [':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'audio', 'math', 'imageGallery'],
                        ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template']
                    ]]
                ],
            };
        },
        helpInit: function (sunEditorForm) {
            const dataCommandHelp = sunEditorForm.querySelector(".se-btn.help-command");
            dataCommandHelp.setAttribute("uk-toggle", "target: #units-help");
            const helpElement = `<div id="units-help" class="uk-flex-top" uk-modal>
                                    <div class="uk-modal-dialog uk-modal-body" style="top: 7%">
                                        <button class="uk-modal-close-default" type="button" uk-close></button>
                                        <h5 class="uk-modal-title">작성 팁</h5>
                                        <div class="mt-15" style="font-size: 14px">
                                        1. 이미지/비디오는 너비 75-100%로 중앙에 위치하는 것이 최적이고, <br>
                                        2. 1개의 이미지는 5MB를 초과하지 말아야 합니다. <br>
                                        3. 여러개 이미지를 사용할 경우 적절한 순서와 배치를 해주세요. <br>
                                        4. 입력줄에 대한 구분이 애매하면, 블록보기를 하여 참고하세요. <br>
                                        5. 프로그래밍 코드를 복사/붙여넣기 할때는, "문단형식[본문]" 탭의 "코드"를 선택하여 작업하면 오류가 발생하지 않아요.
                                        </div>
                                    </div>
                                </div>`;
            sunEditorForm.insertAdjacentHTML("beforeend", helpElement);
        },
        imageVideoRadioButtonInit: function (sunEditorForm) {
            document.body.style.overflow = "unset";

            const dataCommandImage = sunEditorForm.querySelector('[data-command="image"]');
            dataCommandImage.addEventListener("click", function (e) {
                e.preventDefault();
                const imageRadioCheckList = sunEditorForm.querySelectorAll('[name="suneditor_image_radio"]');

                SunEditorUtils.imageVideoCenterRadioCheckReform(imageRadioCheckList);

                const imageRoadWithInput = sunEditorForm.querySelector("input.se-input-control._se_image_size_x");
                // imageRoadWithInput.setAttribute("placeholder", "75%");
                imageRoadWithInput.setAttribute("placeholder", "100%");
                /*아래도 수정*/
                /*let imgSizePercentageBtn = document.querySelector('[data-value="0.75"]');*/
                /*이미지를 에디터에 로드할때 이미지 크기 설정 1=100%, 0.75=75%, 0.5=50%*/

            }, false);

            const dataCommandVideo = sunEditorForm.querySelector('[data-command="video"]');
            dataCommandVideo.addEventListener("click", function (e) {
                e.preventDefault();
                const videoRadioCheckList = sunEditorForm.querySelectorAll('[name="suneditor_video_radio"]');
                SunEditorUtils.imageVideoCenterRadioCheckReform(videoRadioCheckList);

                const videoRoadWithInput = sunEditorForm.querySelector("input.se-input-control._se_video_size_x");
                // videoRoadWithInput.setAttribute("placeholder", "75%");
                videoRoadWithInput.setAttribute("placeholder", "100%");
                /*아래도 수정*/
                /*let videoSizePercentageBtn = document.querySelector('[data-value="0.75"]');*/
                /*이미지를 에디터에 로드할때 이미지 크기 설정 1=100%, 0.75=75%, 0.5=50%*/
            }, false);
        },
        imageVideoCenterRadioCheckReform: function (checkBtnList) {
            checkBtnList.forEach(function (radioCheck, idx) {
                if (radioCheck.getAttribute("value") === "none") {
                    radioCheck.setAttribute("checked", "none");
                    radioCheck.parentElement.style.display = "none";
                }
                if (radioCheck.getAttribute("value") === "center") {
                    radioCheck.click();
                    radioCheck.setAttribute("checked", "checked");
                }

            });
        },
        moreButtonTitleChange: function (sunEditorForm) {
            // https://inpa.tistory.com/entry/JS-%F0%9F%93%9A-windowonload-%EC%A0%95%EB%A6%AC
            window.addEventListener('load', function() {
                const MoreParagraph = sunEditorForm.querySelector('button[data-command="__se__p"] span span');
                const MoreText = sunEditorForm.querySelector('button[data-command="__se__t"] span span');
                const MoreLine = sunEditorForm.querySelector('button[data-command="__se__e"] span span');
                const MoreMisc = sunEditorForm.querySelector('button[data-command="__se__i"] span span');
                const MoreRich = sunEditorForm.querySelector('button[data-command="__se__r"] span span');
                if (MoreParagraph) {
                    MoreParagraph.innerHTML = "문단";
                }
                if (MoreText) {
                    MoreText.innerHTML = "형식";
                }
                if (MoreLine) {
                    MoreLine.innerHTML = "쓰기";
                }
                if (MoreMisc) {
                    MoreMisc.innerHTML = "줄관련";
                }
                if (MoreRich) {
                    MoreRich.innerHTML = "도움말등";
                }
            });
        },
        onImageUploadSize: function (targetElement, state, core, percentBtn) {
            if ((state === "create") && (core.currentControllerName !== "image")) {
                if (core.currentControllerName !== "") {
                    percentBtn.click();
                }
            }
            if ((state === "create") && targetElement.getAttribute('src').includes('base64')) {
                percentBtn.click();
            }
        },
        onVideoUploadSize: function (targetElement, state, core, percentBtn) {
            if ((state === "create") && (core.currentControllerName !== "video")) {
                if (core.currentControllerName !== "") {
                    percentBtn.click();
                }
            }
            if ((state === "create") && targetElement.getAttribute('src').includes('http')) {
                percentBtn.click();
            }
        },
        sunImageSave: function (_url, formData, imgTag) {
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
                        let imgSrc = response.image_path;
                        imgTag.setAttribute('src', '/' + imgSrc);
                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        },
        disableImageUpload: function (modifiedSunEditor) {
            modifiedSunEditor.onImageUploadBefore = function (files, info, core, uploadHandler) {
                alert("이미지는 업로드 할 수 없습니다.");
                return false;
            };
        },

    };

    let others = {
        checkBoxCheck: function () {
            const checkAllBox = document.querySelector("#all-check");
            const checkBoxList = document.querySelectorAll("input.single");
            if (checkAllBox && checkBoxList) {
                othersScript.checkBoxChange(checkAllBox, checkBoxList);
            }
        },
        realDataBoxCheck: function () {
            const relatedDataAllBox = document.querySelector("#all-data");
            const relatedDataBoxList = document.querySelectorAll("input.data");
            if (relatedDataAllBox && relatedDataBoxList) {
                othersScript.checkBoxChange(relatedDataAllBox, relatedDataBoxList);
            }
        },
        checkBoxChange: function (checkAllBox, checkBoxList) {
            checkAllBox. addEventListener("change", function (e) {
                e.preventDefault();
                for (let i = 0; i < checkBoxList.length; i++) {
                    checkBoxList[i].checked = this.checked;
                }
            });

            Array.from(checkBoxList).forEach(function (checkBox) {
                checkBox.addEventListener("change", function (e) {
                    checkAllBox.checked = false;
                });
            });
        },
        intComma: function (num) {
            return Number(num).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        },
        generateRandomString: function (num) {
            const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890αβγδεζηθικλμνξοπρστυφχψω';
            let dateRandom = new Date().getTime().toString(36);
            let mathRandom = Math.random().toString(36).substring(2, 12);
            let result = '';
            const charactersLength = characters.length;
            for (let i = 0; i < num; i++) {
                result += characters.charAt(Math.floor(Math.random() * charactersLength));
            }
            if (currentUserId && currentUsername) {
                return currentUserId + ':~^:' + currentUsername + ';^~;'+ dateRandom + '?'+ result + '&' + mathRandom;
            } else {
                return dateRandom + '?'+ result + '&' + mathRandom;
            }
        },
        existingSelectDelete: function (selectTag) {
            for (let i = 0; i < selectTag.children.length; i++) {
                if (selectTag.children.length > 1 && selectTag.firstChild) {
                    selectTag.removeChild(selectTag.lastChild);
                    i--;
                }
            }
        },
        newSelectInsertIdTitle: function (selectTag, responseObjs) {
            if (selectTag.children.length === 1) {
                responseObjs.forEach(function (list, idx) {
                    let opt = document.createElement('option');
                    opt.setAttribute('value', list.id);
                    opt.innerText = list.title;
                    selectTag.appendChild(opt);
                });
            }
        },
        consoleLog: function (param) {
            console.log(param);
        },

    };

    let module2 = {
        TestFunc: function (param) {
            console.log(param);
            alert('module2 in CommonUtils');
        },
        getInteger: function (num) {
            return num;
        },
    };
    ImageUtils = useInRelatedImage;
    AlertUtils = useInFlashAlert;
    AjaxUtils = useInAjax;
    SunEditorUtils = useInSunEditor;
    othersScript = others;

    module2Utils = module2;
}(window));

function textAreaHeightAuto(obj) {
    obj.style.height = "1px";
    obj.style.height = (12 + obj.scrollHeight) + "px";
}

// common img input(id="image"): image_size check
const imgInput = document.querySelector("#image");
if (imgInput) {
    ImageUtils.imageSizeCheck(imgInput);
}
