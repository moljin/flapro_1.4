"use strict";
/*jshint esversion: 6 */

document.addEventListener('DOMContentLoaded', function () {
    let customPlugin = SunEditorUtils.customPlugIn();
    let baseSetting = SunEditorUtils.baseSetting();
    let commentButtons = SunEditorUtils.commentButtons();
    let SunEditor;

    const commentAlertDiv = document.querySelector(".comment-alert");
    const commentDetailAll = document.querySelectorAll(".comment-detail");
    const commentBtnAll = document.querySelectorAll(".comment-btn");
    const commentDivAll = document.querySelectorAll(".comment");
    console.log("commentDivAll", commentDivAll.length)
    console.log("commentBtnAll", commentBtnAll.length)
    console.log("commentDetailAll", commentDetailAll.length)

    // cancelBtn, submitBtn 은 js로 동적으로 삽입
    commentDivAll.forEach(function (commentDiv, idx) {
        const commentBtn = commentBtnAll[idx];
        const commentDetail = commentDetailAll[idx];

        commentBtn.addEventListener("click", function (e){
            // commentBtn: 새로운 댓글등록 및 기존 댓글수정
            e.preventDefault();
            const targetCommentId = commentBtn.getAttribute("data-comment-id"); // 본문에 대한 기존 comment 수정
            const pairedCommentId = commentBtn.getAttribute("data-paired-id"); // pairedComment 에 대한 기존 replyComment 등록
            // targetCommentId 만 있으면, 본문에 대한 comment update, comment(pairedComment) 에 대한 reply comment update
            // pairedCommentId 만 있으면, pairedComment 에 대한 새로운 replyComment 등록
            // targetCommentId 와 pairedCommentId 둘다 없으면 본문에 대한 초출 Comment 등록
            if (commentBtn.classList.contains("new") || commentBtn.classList.contains("reply")) {
                let ormId = othersScript.generateRandomString(25);
                    commentBtn.setAttribute("data-orm-id", ormId);
                }
            let isSecret;
            let formData = new FormData();
            if (!pairedCommentId) {
                formData.append("comment_id", targetCommentId);
            } else {
                formData.append("paired_comment_id", pairedCommentId);
            }
            let request = $.ajax({
                url: articleCommentIsSecretCheckAjax,
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
                        isSecret = response.is_secret;
                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });

            let commentFormHtml;
            if (isSecret === false) {
                commentFormHtml = `<div class="comment-form">
                                        <div class="suneditor-form">
                                            <div class="suneditor-container">
                                                <textarea id="editorHiddenText" name="content" style="display: none"></textarea>
                                            </div>
                                        </div>
                                        <div class="btn-container pl-15 pr-15 btn-container" uk-grid>
                                            <input type="hidden" name="csrf_token" value=${CSRF_TOKEN}>
                                            <input type="hidden" id="sun_init" name="sun_init" value="article_comment_CU">
                                            <input type="hidden" id="article_id" name="article_id" value=${articleId}>
                                            <div class="left-btn">
                                                <button class="uk-button cancel-btn" uk-tooltip="title: 작성취소; pos: bottom"><i class="fas fa-sync-alt"></i></button>
                                            </div>
                                            <div class="right-btn">
                                                <input hidden type="checkbox" class="secret-checkbox secret-checkbox" name="is_secret">
                                                <button class="uk-button secret-lock" uk-tooltip="title: 비밀글 해제; pos: bottom"><span class="mr-10">비밀글(작성자/관리자 열람)</span><i class="fas fa-lock"></i></button>
                                                <button class="uk-button secret-open" uk-tooltip="title: 비밀글; pos: bottom"><i class="fas fa-lock-open"></i></button>
                                                <button class="uk-button submit" type="button" id="form-submit" uk-tooltip="title: 등록; pos: bottom"><i class="fas fa-comments"></i></button>
                                            </div>
                                        </div>
                                    </div>
                                    `;
            } else {
                commentFormHtml = `<div class="comment-form">
                                        <div class="suneditor-form">
                                            <div class="suneditor-container">
                                                <textarea id="editorHiddenText" name="content" style="display: none"></textarea>
                                            </div>
                                        </div>
                                        <div class="btn-container pl-15 pr-15 btn-container" uk-grid>
                                            <input type="hidden" name="csrf_token" value=${CSRF_TOKEN}>
                                            <input type="hidden" id="sun_init" name="sun_init" value="article_comment_CU">
                                            <input type="hidden" id="article_id" name="article_id" value=${articleId}>
                                            <div class="left-btn">
                                                <button class="uk-button cancel-btn" uk-tooltip="title: 작성취소; pos: bottom"><i class="fas fa-sync-alt"></i></button>
                                            </div>
                                            <div class="right-btn">
                                                <input hidden type="checkbox" class="secret-checkbox secret-checkbox" name="is_secret" checked="checked">
                                                <button class="uk-button secret-lock" style="display: block" uk-tooltip="title: 비밀글 해제; pos: bottom"><span class="mr-10">비밀글(작성자/관리자 열람)</span><i class="fas fa-lock"></i></button>
                                                <button class="uk-button secret-open" style="display: none" uk-tooltip="title: 비밀글; pos: bottom"><i class="fas fa-lock-open"></i></button>
                                                <button class="uk-button submit" type="button" id="form-submit" uk-tooltip="title: 등록; pos: bottom"><i class="fas fa-comments"></i></button>
                                            </div>
                                        </div>
                                    </div>
                                `;
            }

            if (commentAlertDiv.style.display === "block") {
                    AlertUtils.alertRemove(commentAlertDiv);
                }
            const commentFormAll = document.querySelectorAll(".comment-form");
            commentFormAll.forEach(function (comForm){
                comForm.remove();
            });
            commentDivAll.forEach(function (comDiv){
                comDiv.style.display = "none";
            });
            commentBtnAll.forEach(function (comBtn){
                comBtn.style.display = "block";
            });

            commentDetailAll.forEach(function (comDetail){
                let comId = comDetail.getAttribute("data-detail");
                if (targetCommentId === comId) {
                    comDetail.style.display = "none";
                } else {
                    comDetail.style.display = "block";
                }
            });

            commentBtn.style.display = "none";
            commentDiv.style.display = "block";
            commentDiv.insertAdjacentHTML('afterbegin', commentFormHtml);
            SunEditor = SUNEDITOR.create('editorHiddenText',
                Object.assign({}, customPlugin, baseSetting, commentButtons));

            const sunEditorForm = document.querySelector(".suneditor-form");
            const sunEditorEditable = sunEditorForm.querySelector(".se-container .se-wrapper .sun-editor-editable");
            const targetComment = document.querySelector(".detail-" + targetCommentId);
            if (targetComment) {
                sunEditorEditable.innerHTML = targetComment.innerHTML;
            }

            SunEditorUtils.helpInit(sunEditorForm);
            SunEditor.onImageUpload = function (targetElement, index, state, imageInfo, remainingFilesCount, core) {
                // let imgSizePercentageBtn = sunEditorForm.querySelector('[data-value="0.75"]');
                let imgSizePercentageBtn = sunEditorForm.querySelector('[data-value="1"]');
                SunEditorUtils.onImageUploadSize(targetElement, state, core, imgSizePercentageBtn);
            };
            SunEditor.onVideoUpload = function (targetElement, index, state, info, remainingFilesCount, core) {
                // let videoSizePercentageBtn = sunEditorForm.querySelector('[data-value="0.75"]');
                let videoSizePercentageBtn = sunEditorForm.querySelector('[data-value="1"]');
                SunEditorUtils.onVideoUploadSize(targetElement, state, core, videoSizePercentageBtn);
            };
            SunEditorUtils.imageVideoRadioButtonInit(sunEditorForm);

            const secretCheckbox = document.querySelector(".secret-checkbox");
            const secretLock = document.querySelector(".btn-container .secret-lock");
            const secretOpen = document.querySelector(".btn-container .secret-open");
            secretLock.addEventListener("click", function (e) {
                e.preventDefault();
                secretCheckbox.removeAttribute("checked");
                secretOpen.style.display = "block";
                secretLock.style.display = "none";
            }, false);
            secretOpen.addEventListener("click", function (e) {
                e.preventDefault();
                secretCheckbox.setAttribute("checked", "checked");
                secretOpen.style.display = "none";
                secretLock.style.display = "block";
            }, false);


            const cancelBtn = document.querySelector(".left-btn .cancel-btn");
            const commentForm = document.querySelector(".comment-form");
            cancelBtn.addEventListener("click", function (e){
                commentForm.remove();
                commentBtn.style.display = "block";
                commentDiv.style.display = "none";
                commentDetail.style.display = "block";
            });

            const commentDeleteModalHtml = `<button class="comment-delete-modal-btn uk-button" uk-toggle="target: #comment-delete-modal" uk-tooltip="title: 댓글삭제; pos: bottom">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                            <div id="comment-delete-modal" class="uk-flex-top" uk-modal>
                                                <div class="uk-modal-dialog uk-modal-body uk-margin-auto-vertical">
                                                    <button class="uk-modal-close-default" type="button" uk-close></button>
                                                    정말로 댓글을 삭제하시겠어요?
                                                    <input type="hidden" name="csrf_token" value="${CSRF_TOKEN}">
                                                    <input type="hidden" id="comment_id" value="${targetCommentId}">
                                                    <div class="btn uk-inline ml-15 uk-align-right">
                                                        <button class="comment-delete-btn uk-button uk-button-primary mt-40" id="comment-delete-btn" type="button">삭제</button>
                                                    </div>
                                                </div>
                                            </div>
                                            `;
            const cancelDeleteContainerLeftBtn = document.querySelector(".left-btn");
            if (commentDetail.getAttribute("data-detail") === targetCommentId) {
                cancelDeleteContainerLeftBtn.insertAdjacentHTML("beforeend", commentDeleteModalHtml);
            }
            const commentDeleteBtn = document.querySelector(".comment-delete-btn");
            if (commentDeleteBtn) {
                commentDeleteBtn.addEventListener("click", function (e) {
                    let formData = new FormData();
                    formData.append("comment_id", targetCommentId);
                    let url = articleCommentDeleteAjax;
                    let type = "successRedirect";
                    AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, null, type, null);
                }, false);
            }

            const sunSubmit = document.querySelector("#form-submit");
            sunSubmit.addEventListener("click", function (e){
                e.preventDefault();
                const sunInit = document.querySelector("#sun_init").value;
                const articleId = document.querySelector("#article_id").value;
                const isSecret = document.querySelector(".secret-checkbox").checked;
                const ormId = commentBtn.getAttribute("data-orm-id");
                sunEditorImageListSave(sunInit, ormId, articleId);

                document.getElementById('editorHiddenText').value = SunEditor.getContents();
                const commentContent = document.getElementById('editorHiddenText').value;
                if (targetCommentId) { // 본문에 대한 comment update, comment(pairedComment) 에 대한 reply comment update
                    sunEditorContentSave(sunInit, articleId, targetCommentId, ormId, isSecret, commentContent);
                }
                else if (pairedCommentId) { // comment(pairedComment) 에 대한 reply comment create
                    sunEditorContentSave(sunInit, articleId, pairedCommentId, ormId, isSecret, commentContent);
                } else { //본문에 대한 초출 comment create
                    sunEditorContentSave(sunInit, articleId, null , ormId, isSecret, commentContent);
                }
            },false);

            function sunEditorContentSave(sunInit, articleId, commentId, ormId, isSecret, commentContent) {
                let formData = new FormData();
                formData.append("sun_init", sunInit);
                formData.append("article_id", articleId);
                if (targetCommentId) {
                    formData.append("comment_id", commentId);
                } else if (pairedCommentId) {
                    formData.append("paired_comment_id", commentId);
                } else {
                    formData.append("comment_id", commentId);
                }
                formData.append("orm_id", ormId);
                formData.append("is_secret", isSecret);
                formData.append("content", commentContent);
                let url = articleCommentSave;
                let type = "requestGetParam";
                AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, commentAlertDiv, type, null);
            }

            function sunEditorImageListSave(sunInit, ormId, _articleId) {
                const sunEditorEditable = sunEditorForm.querySelector(".se-container .se-wrapper .sun-editor-editable");

                let imgTagList = sunEditorEditable.querySelectorAll('img');
                imgTagList.forEach(function (imgTag) {
                    if (imgTag.getAttribute('src').includes('base64')) {
                        let fileName = imgTag.getAttribute('data-file-name');
                        let block = imgTag.getAttribute('src').split(';');
                        let realData = block[1].split(',')[1]; // 이 경우 '/gj.........Tf/5z0L/2vs1lb4eGcnUco//Z'

                        /*product_comment_CU 등도 추가될 예정*/
                        let articleId;
                        if (sunInit === "article_comment_CU") {
                            articleId = _articleId;
                        }

                        let formData = new FormData();
                        formData.append('sun_init', sunInit);
                        formData.append('upload_img', realData); // 이미지의 Blob를 폼 데이터 객체에 추가
                        formData.append('file_name', fileName);
                        formData.append('orm_id', ormId);

                        /*product_comment_CU 등도 추가될 예정*/
                        if (sunInit === "article_comment_CU") {
                            formData.append('article_id', articleId);
                        }
                        let url = editorImagesSaveAjax;
                        SunEditorUtils.sunImageSave(url, formData, imgTag);
                    }
                });
            }

        },false);

    });

});

