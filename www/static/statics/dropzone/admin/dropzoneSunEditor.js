"use strict"
/*jshint esversion: 6 */
// https://yohanpro.com/posts/codereview/2
// https://inpa.tistory.com/entry/Dropzone-%F0%9F%93%9A-%EC%9D%B4%EB%AF%B8%EC%A7%80-%ED%8C%8C%EC%9D%BC-%EC%97%85%EB%A1%9C%EB%93%9C-%EB%93%9C%EB%9E%98%EA%B7%B8-%EC%95%A4-%EB%93%9C%EB%A1%AD-%EB%9D%BC%EC%9D%B4%EB%B8%8C%EB%9F%AC%EB%A6%AC-%EC%82%AC%EC%9A%A9%EB%B2%95#dropzone_%EC%BB%A4%EC%8A%A4%ED%85%80_%ED%85%9C%ED%94%8C%EB%A6%BF

Dropzone.autoDiscover = false;
document.addEventListener('DOMContentLoaded', function () {

    let SimpleSunEditor;
    const simpleSunEditorBaseSet = SunEditorUtils.baseSetting();
    const simpleSunEditorButton = SunEditorUtils.simpleButtons();

    let DropZoneUploader;

    const removeBtn = `<button class="uk-button uk-button-default dz-remove-btn" type="button"><i class="fas fa-trash-alt"></i></button>`;
    const reviewSaveUrl = productReviewSave;

    const DropZoneBaseSet = dropzoneSet.dzBaseSet(reviewSaveUrl, removeBtn);

    const DropZoneFuncSet = {
        init: function () {
            let dropZone = this;
            let addedFiles = []; //중복된 파일 제거하고, 중복되지 않는 파일 담아놓는 임시 리스트
            let fileDict = {};
            const boardIdInputTag = document.querySelector("#board_id");

            const boardSubmitBtn = document.querySelector("#form-submit");
            // const contentEditable = document.querySelector(".contentEditable");

            let currentPath = document.location.href;
            boardSubmitBtn.addEventListener("click", function (e) {
                fileDict.images = addedFiles; //없어도 된다.
                DropZoneUploader.files = addedFiles; //없어도 된다.
                // document.querySelector("#content-textarea").innerHTML = contentEditable.innerHTML;
                const sunEditorForm = document.querySelector(".simpleEditor-form");
                const sunEditorEditable = sunEditorForm.querySelector(".se-container .se-wrapper .sun-editor-editable");
                document.querySelector("#editorHiddenText").innerHTML = sunEditorEditable.innerHTML;

                if (dropZone.files.length === 0) {
                    let _url = reviewSaveUrl;
                    let dzAlertDiv = document.querySelector(".dz-alert");
                    let type = "successRedirect";
                    let formData = new FormData();
                    // DropZoneFormData(formData);
                    dropzoneSet.dzFormData(formData, currentPath, boardIdInputTag);
                    AjaxUtils.flashMessageRedirectRemoveDiv(_url, formData, null, type, null);
                } else {
                    DropZoneUploader.processQueue();
                }

            }, false);

            dropzoneSet.dzSendingFunc(dropZone, currentPath, boardIdInputTag);
            // dropZone.on("sending", function (file, xhr, formData) {
            //     DropZoneFormData(formData);
            //     // dropzoneSet.dzFormData(formData, currentPath, reviewIdInputTag);
            // });

            // function DropZoneFormData(formData) {
            //     formData.append("current_path", currentPath);
            //     formData.append("review_id", reviewIdInputTag.value);
            //     formData.append("user_id", document.querySelector("#user_id").value);
            //     formData.append("product_id", document.querySelector("#product_id").value);
            //     // formData.append("content", document.querySelector("#content-textarea").value);
            //     formData.append("content", document.querySelector("#editorHiddenText").value);
            // }

            let successCount = 0;
            dropzoneSet.dzFuncSet(dropZone, addedFiles, successCount);

            // dropZone.on('addedfile', function (file) {
            //     /*중복된 파일의 제거*/
            //     if (dropZone.files.length) {
            //         let hasFile = false;
            //         for (let i = 0; i < dropZone.files.length - 1; i++) {
            //             if (
            //                 dropZone.files[i].name === file.name &&
            //                 dropZone.files[i].size === file.size &&
            //                 dropZone.files[i].lastModifiedDate.toString() === file.lastModifiedDate.toString()
            //             ) {
            //                 hasFile = true;
            //                 dropZone.removeFile(file);
            //             }
            //         }
            //         if (!hasFile) {
            //             addedFiles.push(file);
            //         }
            //     } else {
            //         addedFiles.push(file);
            //     }
            //     console.log("dropZone.files", dropZone.files);
            // });
            //
            // dropZone.on("removedfile", function (file) {
            //     console.log("removedfile", file);
            // });
            //
            // dropZone.on("success", function (file, response, progressEvent) {
            //     if (file.accepted) {
            //         successCount++;
            //     }
            //
            //     if (dropZone.files.length === successCount) {
            //         console.log(successCount);
            //     }
            //     let oldAlertDiv = document.querySelector(".old-alert-" + boardIdInputTag.value);
            //     /*
            //     const flashParentDivAll = document.querySelectorAll(".flash-parent");
            //     const pairedOldAlertDiv = document.querySelector(".old-alert-" + boardIdInputTag.value);
            //     flashParentDivAll.forEach(function (flashParent, j) {
            //        console.log(flashParent)
            //        if (flashParent.classList.contains("old-alert-" + boardIdInputTag.value)) {
            //           console.log(flashParent)
            //
            //           flashParent.remove();
            //        }
            //        alert("")
            //     });
            //     */
            //     // window.location.href = response.redirect_url;
            //     window.location.assign(response.redirect_url);
            //     // alert(response.flash_message); // only this method  여러장인경우 거슬림
            //     window.location.reload(); // window.location.reload(true); //true 가 없어도 된다.
            //     // setTimeout(AlertUtils.alertDisplay, 1000, oldAlertDiv, response.flash_message);
            //     // AlertUtils.alertDisplay(oldAlertDiv, response.flash_message);
            //     // console.log(progressEvent)
            //     // console.log(res_html)
            // });
            //
            // dropZone.on("error", function (file, res_html) {
            //     const errorMessageTagList = document.querySelectorAll(".dz-error-message span");
            //     errorMessageTagList.forEach(function (messageTag, idx) {
            //         messageTag.innerHTML = "업로드가 완료되지 않았어요!!";
            //     });
            //     console.log("error", file);
            //     // console.log(res_html)
            // });
            //
            // dropZone.on("processingmultiple", function (fileList) {
            //     console.log("processingmultiple", fileList);
            // });
            //
            // dropZone.on("sendingmultiple", function (fileList) {
            //     console.log("sendingmultiple", fileList);
            // });

        },
    };

    DropZoneUploader = new Dropzone("div.dropzone",
        Object.assign({}, DropZoneBaseSet, DropZoneFuncSet));

    SimpleSunEditor = SUNEDITOR.create('editorHiddenText',
        Object.assign({}, simpleSunEditorBaseSet, simpleSunEditorButton));

    SunEditorUtils.disableImageUpload(SimpleSunEditor);

    /*기존 dropzone 이미지 삭제버튼 활성화 및 삭제구현*/
    const targetReviewId = document.querySelector("#board_id").value;
    const targetOldImageContainer = document.querySelector(".image-" + targetReviewId);
    if (targetOldImageContainer) {
        let oldImgRemoveBtnAll = targetOldImageContainer.querySelectorAll(".old-img-remove-btn");
        let oldImgDeleteBtnAll = targetOldImageContainer.querySelectorAll(".old-img-delete-btn");
        oldImgDeleteBtnAll.forEach(function (deleteBtn, ix) {
            deleteBtn.addEventListener("click", function (ev) {
                ev.preventDefault();
                oldImgDeleteBtnAll.forEach(function (delBtn) {
                    if (delBtn.children[0].classList.contains("fa-check")) {
                        delBtn.innerHTML = `<i class="fas fa-trash-alt"><!--삭제--></i>`;
                    }
                });

                deleteBtn.innerHTML = `<i class="fas fa-check"></i>`;
                let checkHtml = `<div class="response-container">
                                      정말로 이미지를 삭제하시겠어요?
                                      <div class="btn mt-15 uk-text-right"><button class="delete-confirm-btn uk-button" type="button">삭제</button></div>
                                   </div>`;

                let url = productReviewDzImageDeleteAjax;
                let alertDiv = document.querySelector(".dz-alert");
                let targetDzImageObjId = deleteBtn.getAttribute("data-id");

                let checkFormData = new FormData();
                checkFormData.append('checked', "confirm");
                checkFormData.append('review_id', targetReviewId);
                checkFormData.append('image_id', targetDzImageObjId);
                let request = $.ajax({
                    url: url,
                    type: 'POST',
                    data: checkFormData,
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
                            if (response.flash_message === response._success + ":" + targetReviewId + ":" + targetDzImageObjId)
                                AlertUtils.alertDisplay(alertDiv, checkHtml);

                            const alertCloseBtn = alertDiv.querySelector(".uk-alert-close");
                            alertCloseBtn.addEventListener("click", function (eve) {
                                eve.preventDefault();
                                oldImgDeleteBtnAll.forEach(function (delBtn) {
                                    if (delBtn.children[0].classList.contains("fa-check")) {
                                        delBtn.innerHTML = `<i class="fas fa-trash-alt"><!--삭제--></i>`;
                                    }
                                });
                            });

                            const deleteConfirmBtn = alertDiv.querySelector(".delete-confirm-btn");
                            deleteConfirmBtn.addEventListener("click", function (event) {
                                event.preventDefault();
                                let _type = "flashMessageRemoveDiv";
                                let removeOldImageLi = document.querySelector(".old-image-li-" + targetDzImageObjId);

                                let formData = new FormData();
                                formData.append('image_id', targetDzImageObjId);
                                AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, alertDiv, _type, removeOldImageLi);
                            }, false);
                        }
                    },
                    error: function (err) {
                        AjaxUtils.serverErrorAlert(err);
                    }
                });


            }, false);
        });
    }

    const reviewDeleteBtn = document.querySelector("#review-delete-btn");
    reviewDeleteBtn.addEventListener("click", function (e) {
        let currentPath = document.location.href;
        let formData = new FormData();
        formData.append("review_id", targetReviewId);
        formData.append("current_path", currentPath);
        let url = productReviewDeleteAjax;
        let type = "successRedirect";
        AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, null, type, null);
    }, false);


});
