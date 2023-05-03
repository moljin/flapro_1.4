"use strict"
/*jshint esversion: 6 */
// https://yohanpro.com/posts/codereview/2
// https://inpa.tistory.com/entry/Dropzone-%F0%9F%93%9A-%EC%9D%B4%EB%AF%B8%EC%A7%80-%ED%8C%8C%EC%9D%BC-%EC%97%85%EB%A1%9C%EB%93%9C-%EB%93%9C%EB%9E%98%EA%B7%B8-%EC%95%A4-%EB%93%9C%EB%A1%AD-%EB%9D%BC%EC%9D%B4%EB%B8%8C%EB%9F%AC%EB%A6%AC-%EC%82%AC%EC%9A%A9%EB%B2%95#dropzone_%EC%BB%A4%EC%8A%A4%ED%85%80_%ED%85%9C%ED%94%8C%EB%A6%BF

Dropzone.autoDiscover = false;
document.addEventListener('DOMContentLoaded', function () {
   let SimpleSunEditor;
   const simpleSunEditorBaseSet = SunEditorUtils.baseSetting();
   const simpleSunEditorButton = SunEditorUtils.simpleButtons();

   /*################### Product Review Using DropZone and SunEditor ######################*/
   let DropZoneUploader;

   const removeBtn = `<button class="uk-button uk-button-default dz-remove-btn" type="button"><i class="fas fa-trash-alt"></i></button>`;
   const reviewSaveUrl = productReviewSave;
   const DropZoneBaseSet = {
                url: reviewSaveUrl,
                method: 'POST',
                headers: {"X-CSRF-Token": CSRF_TOKEN,},
                autoProcessQueue: false,
                acceptedFiles: "image/*", // ".jpeg,.jpg,.png,.gif,.bmp,.tif",
                uploadMultiple: true,  // 이거를 넣으면 request.files.getlist("image")이 잡히지 않는다.
                paramName: 'image',  //기본은 'file'
                addRemoveLinks: true,
                // dictRemoveFile: '삭제',
                // dictCancelUpload: '취소', //'취소'
                dictRemoveFile: removeBtn,
                dictCancelUpload: removeBtn, //'취소'
                parallelUploads: 100,
            };

   const DropZoneFuncSet = {
      init: function () {
         let dropZone = this;
         let addedFiles = []; //중복된 파일 제거하고, 중복되지 않는 파일 담아놓는 임시 리스트
         let fileDict = {};
         const boardIdInputTag = document.querySelector("#board_id");
         const boardSubmitBtn = document.querySelector("#board-submit");

         let currentPath = document.location.href;
         boardSubmitBtn.addEventListener("click", function (e) {
            fileDict.images = addedFiles; //없어도 된다.
            DropZoneUploader.files = addedFiles; //없어도 된다.
            // document.querySelector("#content-textarea").innerHTML = contentEditable.innerHTML;
            const sunEditorForm = document.querySelector(".simpleEditor-form");
            const sunEditorEditable = sunEditorForm.querySelector(".se-container .se-wrapper .sun-editor-editable");
            document.querySelector("#editorHiddenText").innerHTML = sunEditorEditable.innerHTML;

            if (dropZone.files.length === 0) {
               /*dropZone 에 이미지를 넣지않으면 SunEditor 만 저장된다.*/
               let _url = reviewSaveUrl;
               let dzAlertDiv = document.querySelector(".dz-alert");
               let type = "successRedirect";
               let formData = new FormData();
               // dropzoneSet.dzFormData(formData, currentPath, boardIdInputTag);
               DropZoneFormData(formData);
               AjaxUtils.flashMessageRedirectRemoveDiv(_url, formData, null, type, null);
            } else {
               /*dropZone 에 이미지를 넣으면 DropZoneBaseSet url 타고 저장된다.*/
               DropZoneUploader.processQueue();
            }

         }, false);
         // dropzoneSet.dzSendingFunc(dropZone, currentPath, boardIdInputTag);
         dropZone.on("sending", function (file, xhr, formData) {
            // dropzoneSet.dzFormData(formData, currentPath, boardIdInputTag);
            DropZoneFormData(formData);
         });

         function DropZoneFormData (formData) {
            formData.append("current_path", currentPath);
            formData.append("review_id", boardIdInputTag.value);
            formData.append("user_id", document.querySelector("#user_id").value);
            formData.append("product_id", document.querySelector("#product_id").value);
            // formData.append("content", document.querySelector("#content-textarea").value);
            formData.append("content", document.querySelector("#editorHiddenText").value);
         }

         // let successCount = 0;
         // dropzoneSet.dzFuncSet(dropZone, addedFiles, successCount);

         dropZone.on('addedfile', function (file) {
            /*중복된 파일의 제거*/
            if (dropZone.files.length) {
               let hasFile = false;
               for (let i = 0; i < dropZone.files.length - 1; i++) {
                  if (
                      dropZone.files[i].name === file.name &&
                      dropZone.files[i].size === file.size &&
                      dropZone.files[i].lastModifiedDate.toString() === file.lastModifiedDate.toString()
                  ) {
                     hasFile = true;
                     dropZone.removeFile(file);
                  }
               }
               if (!hasFile) {
                  addedFiles.push(file);
               }
            } else {
               addedFiles.push(file);
            }
            console.log("dropZone.files", dropZone.files);
         });

         dropZone.on("removedfile", function (file) {
            console.log("removedfile", file);
         });

         let successCount = 0;
         dropZone.on("success", function (file, response, progressEvent) {
            if (file.accepted) {
               successCount++;
            }

            if (dropZone.files.length === successCount) {
               console.log(successCount);
            }
            let oldAlertDiv = document.querySelector(".old-alert-"+boardIdInputTag.value);
            /*
            const flashParentDivAll = document.querySelectorAll(".flash-parent");
            const pairedOldAlertDiv = document.querySelector(".old-alert-" + boardIdInputTag.value);
            flashParentDivAll.forEach(function (flashParent, j) {
               console.log(flashParent)
               if (flashParent.classList.contains("old-alert-" + boardIdInputTag.value)) {
                  console.log(flashParent)

                  flashParent.remove();
               }
               alert("")
            });
            */
            // window.location.href = response.redirect_url;
            window.location.assign(response.redirect_url);
            window.location.reload(); // window.location.reload(true); //true 가 없어도 된다.
            // setTimeout(AlertUtils.alertDisplay, 1000, oldAlertDiv, response.flash_message);
            // AlertUtils.alertDisplay(oldAlertDiv, response.flash_message);
            // console.log(progressEvent)
            // console.log(res_html)
         });

         dropZone.on("error", function (file, res_html){
            const errorMessageTagList = document.querySelectorAll(".dz-error-message span");
            errorMessageTagList.forEach(function (messageTag, idx){
               messageTag.innerHTML = "업로드가 완료되지 않았어요!!";
            });
             console.log("error", file);
            // console.log(res_html)
         });

         dropZone.on("processingmultiple", function (fileList) {
            console.log("processingmultiple", fileList);
         });

         dropZone.on("sendingmultiple", function (fileList){
             console.log("sendingmultiple", fileList);
         });

      },
   };

   const dzRelatedContainerList = document.querySelectorAll(".dz-related-container");

   const dzOldImageDivAll = document.querySelectorAll(".dz-old-image");
   const dzOldContentDivAll = document.querySelectorAll(".dz-old-content");
   const editButtonsAll = document.querySelectorAll(".edit-buttons");
   const dzBtnAll = document.querySelectorAll(".dz-btn");
   const dzEditCancelBtnAll = document.querySelectorAll(".dz-edit-cancel-btn");
   const dzDeleteModalBtnAll = document.querySelectorAll(".dz-delete-modal-btn");
   const dzDeleteBtnAll = document.querySelectorAll(".dz-delete-btn");

   dzRelatedContainerList.forEach(function (dzRelatedContainer, idx){
      const editButtons = editButtonsAll[idx];
      const dzBtn = dzBtnAll[idx];
      const dzOldImageDiv = dzOldImageDivAll[idx];
      const dzOldContentDiv = dzOldContentDivAll[idx];
      const dzEditCancelBtn = dzEditCancelBtnAll[idx];
      const dzDeleteModalBtn = dzDeleteModalBtnAll[idx];
      const dzDeleteBtn = dzDeleteBtnAll[idx];

      const targetReviewId = dzRelatedContainer.getAttribute("id");

      dzBtn.addEventListener("click", function (e){
         e.preventDefault();

         dropZoneRelatedReset();
         questionContentReset();
         QnaRelatedReset();

         editButtons.classList.add("border");
         dzBtn.style.display = "none";
         dzEditCancelBtn.style.display = "block";
         dzDeleteModalBtn.style.display = "block";

         const DropZoneForHtml = `<div class="dz-related-form">
                                      <div class="dz-alert"></div>
                                      <div class="dz-container">
                                           <div class="dropzone">
                                               <div class="dz-message" data-dz-message>
                                                   <span class="placeholder" data-placeholder="클릭"></span>
                                               </div>
                                           </div>
                                       </div>
                                       <div class="related-container mt-10">
                                           <div class="simpleEditor-form">
                                                <div class="simpleEditor-container">
                                                    <textarea id="editorHiddenText" name="content" style="display: none"></textarea>
                                                </div>
                                         </div>
                                       </div>
                                       <div class="submit-container">
                                           <input type="hidden" id="user_id" name="user_id" value="${currentUserId}">
                                           <input type="hidden" id="product_id" name="product_id" value="${targetProductId}">
                                           <input type="hidden" id="board_id" name="board_id" value="">
                                           <button type="button" class="uk-button uk-button-default mr-20" id="board-submit" uk-tooltip="title: 저장; pos: bottom"><i class="fas fa-cloud-upload-alt"></i></button>
                                       </div>
                                </div>`;

         /*Dropzone Related 생성 ###############################*/
         dzRelatedContainer.style.display = "block";
         dzRelatedContainer.insertAdjacentHTML('afterbegin', DropZoneForHtml);
         DropZoneUploader = new Dropzone("div.dropzone",
            Object.assign({}, DropZoneBaseSet, DropZoneFuncSet));
         /*SimpleSunEditor 생성 ################################*/
         SimpleSunEditor = SUNEDITOR.create('editorHiddenText',
             Object.assign({}, simpleSunEditorBaseSet, simpleSunEditorButton));

         SunEditorUtils.disableImageUpload(SimpleSunEditor);

         /*기존 내용 편집창 안에 넣고, 기존내용 display none*/
         const boardIdInputTag = document.querySelector("#board_id");
         const sunEditorForm = document.querySelector(".simpleEditor-form");
         const sunEditorEditable = sunEditorForm.querySelector(".se-container .se-wrapper .sun-editor-editable");
         const targetContent = document.querySelector(".content-detail-"+targetReviewId);
         boardIdInputTag.value = targetReviewId;
         /*바로 전 닫아놓았던 기존내용 display none ===> block*/
         dzOldContentDivAll.forEach(function (dzOldContent) {
               if (dzOldContent.style.display === "none") {
                  dzOldContent.style.display = "block";
               }
            });
         if (targetContent) {
            sunEditorEditable.innerHTML = targetContent.innerHTML;
            targetContent.style.display = "none";
         }

         /*기존 dropzone 이미지 삭제버튼 활성화 및 삭제구현*/
         const targetOldImageContainer = document.querySelector(".image-"+targetReviewId);
         if (targetOldImageContainer) {
            let oldImgRemoveBtnAll = targetOldImageContainer.querySelectorAll(".old-img-remove-btn");
            let oldImgDeleteBtnAll = targetOldImageContainer.querySelectorAll(".old-img-delete-btn");
            oldImgDeleteBtnAll.forEach(function (deleteBtn, ix) {
               deleteBtn.style.display = "block";
               deleteBtn.addEventListener("click", function (ev) {
                  ev.preventDefault();
                  oldImgDeleteBtnAll.forEach(function (delBtn){
                     if (delBtn.children[0].classList.contains("fa-check")) {
                        delBtn.innerHTML = `<i class="fas fa-trash-alt"><!--삭제--></i>`;
                     }
                  });

                  deleteBtn.innerHTML = `<i class="fas fa-check"></i>`;
                  let checkHtml = `<div class="response-container">
                                      정말로 이미지를 삭제하시겠어요?
                                      <div class="btn mt-15"><button class="delete-confirm-btn uk-button" type="button">삭제</button></div>
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
                           if (response.flash_message === response._success+":"+targetReviewId+":"+targetDzImageObjId)
                              AlertUtils.alertDisplay(alertDiv, checkHtml);

                              const alertCloseBtn = alertDiv.querySelector(".uk-alert-close");
                              alertCloseBtn.addEventListener("click", function (eve){
                                 eve.preventDefault();
                                 oldImgDeleteBtnAll.forEach(function (delBtn) {
                                    if (delBtn.children[0].classList.contains("fa-check")) {
                                       delBtn.innerHTML = `<i class="fas fa-trash-alt"><!--삭제--></i>`;
                                    }
                                 });
                              });

                              const deleteConfirmBtn = alertDiv.querySelector(".delete-confirm-btn");
                              deleteConfirmBtn.addEventListener("click", function (event){
                                 event.preventDefault();
                                 let _type = "flashMessageRemoveDiv";
                                 let removeOldImageLi = document.querySelector(".old-image-li-" + targetDzImageObjId);

                                 let formData = new FormData();
                                 formData.append('image_id', targetDzImageObjId);
                                 AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, alertDiv, _type, removeOldImageLi);
                              },false);
                        }
                     },
                     error: function (err) {
                        AjaxUtils.serverErrorAlert(err);
                     }
                  });



               }, false);
            });
         }

         /*cancel*/
         dzEditCancelBtn.addEventListener("click", function (e) {
            let dzAlertDiv = document.querySelector(".dz-alert");
            if (dzAlertDiv) {
               if (dzAlertDiv.style.display === "block") {
                  AlertUtils.alertRemove(dzAlertDiv);
               }
            }

            dzBtn.style.display = "block";
            dzEditCancelBtn.style.display = "none";
            dzDeleteModalBtn.style.display = "none";
            dzRelatedContainer.innerHTML = "";
            dzRelatedContainer.style.display = "none";
            if (targetContent) {
               targetContent.style.display = "block";
            }
            if (targetOldImageContainer) {
               let oldImgDeleteBtnAll = targetOldImageContainer.querySelectorAll(".old-img-delete-btn");
               oldImgDeleteBtnAll.forEach(function (delBtn) {
                  if (delBtn.children[0].classList.contains("fa-check")) {
                     delBtn.innerHTML = `<i class="fas fa-trash-alt"><!--삭제--></i>`;
                  }
                  delBtn.style.display = "none";
               });
            }
            editButtonsAll.forEach(function (editButtons) {
               if (editButtons.classList.contains("border")) {
                  editButtons.classList.remove("border");
               }
            });
         },false);

         dzDeleteBtn.addEventListener("click", function (e) {
            let currentPath = document.location.href;
            let formData = new FormData();
            formData.append("review_id", targetReviewId);
            formData.append("current_path", currentPath);
            let url = productReviewDeleteAjax;
            let type = "successRedirect";
            AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, null, type, null);
         },false);

      });

   });

   function dropZoneRelatedReset() {
      dzRelatedContainerList.forEach(function (dzRelatedContainer) {
         if (dzRelatedContainer.style.display === "block") {
            dzRelatedContainer.style.display = "none";
         }
      });
      dzBtnAll.forEach(function (dropzoneBtn) {
         if (dropzoneBtn.style.display === "none") {
            dropzoneBtn.style.display = "block";
         }
      });
      editButtonsAll.forEach(function (editButtons) {
         if (editButtons.classList.contains("border")) {
            editButtons.classList.remove("border");
         }
      });
      dzEditCancelBtnAll.forEach(function (cancelBtn) {
         if (cancelBtn.style.display === "block") {
            cancelBtn.style.display = "none";
         }
      });

      dzDeleteModalBtnAll.forEach(function (deleteModalBtn) {
         if (deleteModalBtn.style.display === "block") {
            deleteModalBtn.style.display = "none";
         }
      });

      /*열려있는 alert div remove*/
      let dzAlertDiv = document.querySelector(".dz-alert");
      if (dzAlertDiv) {
         AlertUtils.alertRemove(dzAlertDiv);
      }

      /*동적 삽입된 DropZoneForHtml remove 와 기존 dropzone 이미지 삭제버튼 display none */
      const existingDzRelatedForm = document.querySelector(".dz-related-form");
      const totalOldImgDeleteBtnAll = document.querySelectorAll(".old-img-delete-btn");
      if (existingDzRelatedForm) {
         existingDzRelatedForm.remove();
         totalOldImgDeleteBtnAll.forEach(function (deleteBtn) {
            if (deleteBtn.style.display === "block") {
               deleteBtn.style.display = "none";
            }
         });
      }
   }

   /*################### Product QNA using SunEditor ######################*/
   const questionBtn = document.querySelector(".question-btn");
   const questionFormContainer = document.querySelector(".question-form-container");
   const questionHtml = `<div class="question-form">
                                <form action=${productQuestionSave} method="POST" enctype="multipart/form-data">
                                    <div class="secret-type">
                                        <div class="secret">
                                            <input type="checkbox" class="uk-checkbox mr-5" id="is_secret" name="is_secret"> 비밀글
                                        </div>
                                        <div class="type ml-20">
                                            <select id="question_type" name="question_type" class="uk-select type">
                                                <option value="">--- 문의유형 ---</option>
                                                <option value="상품" selected>상품</option>
                                                <option value="배송">배송</option>
                                                <option value="반품/취소">반품/취소</option>
                                                <option value="교환/변경">교환/변경</option>
                                                <option value="기타">기타</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="title mt-5">
                                        <div>
                                            <input type="text" maxlength="60" class="uk-input" id="question_title" name="title" placeholder="제목" required>
                                        </div>
                                    </div>
                                    <div class="editor-container mt-5">
                                       <div class="simpleEditor-form">
                                            <div class="simpleEditor-container">
                                                <textarea id="editorHiddenText" name="content" style="display: none"></textarea>
                                            </div>
                                     </div>
                                   </div>
                                   <div class="btn-container">
                                        <input type="hidden" id="question_user_id" name="user_id" value="${currentUserId}">
                                        <input type="hidden" id="question_product_id" name="product_id" value="${targetProductId}">
                                        <input type="hidden" id="question_id" name="question_id" value="">
                                        <input type="hidden" name="csrf_token" value="${CSRF_TOKEN}">
                                        <input type="hidden" id="current_path" name="current_path" value="${currentFullPath}">
                                        <button class="question-cancel-btn uk-button uk-button-default" type="button" uk-tooltip="title: 작성취소; pos: bottom">
                                            <i class="fas fa-sync-alt"><!--작성 취소--></i>
                                        </button>
                                        <button class="uk-button uk-button-default" type="submit" id="question-submit" uk-tooltip="title: 저장; pos: bottom"><i class="fas fa-save"><!--저장--></i></button>
                                    </div>
                                </form>
                            </div>`;

   const tableTbodyTrTagAll = document.querySelectorAll("tbody tr");
   const replyBtnAll = document.querySelectorAll(".reply-btn");
   const questionUpdateBtnAll = document.querySelectorAll(".question-update-btn");
   const replyUpdateBtnAll = document.querySelectorAll(".reply-update-btn");

   /*New Question Create*/
   if (questionBtn) {
      questionBtn.addEventListener("click", function (e) {

         questionContentReset();
         dropZoneRelatedReset();
         QnaRelatedReset();

         /* relatedQuestionFormReset(existingQuestionForm);에서 block 을 했으므로 뒤에서 다시 none */
         questionBtn.style.display = "none";
         questionFormContainer.insertAdjacentHTML("afterbegin", questionHtml);
         /*SimpleSunEditor 생성 ################################*/
         SimpleSunEditor = SUNEDITOR.create('editorHiddenText',
             Object.assign({}, simpleSunEditorBaseSet, simpleSunEditorButton));

         SunEditorUtils.disableImageUpload(SimpleSunEditor);

         const questionCancelBtn = document.querySelector(".question-cancel-btn");
         questionCancelBtn.addEventListener("click", function (e) {
            const existingQuestionForm = document.querySelector(".question-form");
            if (existingQuestionForm) {
               existingQuestionForm.remove();
            }
            questionBtn.style.display = "block";
         }, false);

         const submitBtn = document.querySelector("#question-submit");
         const sunEditorForm = document.querySelector(".simpleEditor-form");
         const sunEditorEditable = sunEditorForm.querySelector(".se-container .se-wrapper .sun-editor-editable");
         submitBtn.addEventListener("click", function (e) {
            document.querySelector("#editorHiddenText").innerHTML = sunEditorEditable.innerHTML;
         }, false);

      }, false);
   }

   /*Question Update*/
   const questionLinkTitleAll = document.querySelectorAll(".question-link.title");
   const questionContentQuestionAll = document.querySelectorAll(".question-content .question");
   const questionContentQuestionInnerAll = document.querySelectorAll(".question-content .question .inner");
   const questionContentInnerContentAll = document.querySelectorAll(".question-content .question .inner .content");
   const questionDeleteContainerAll = document.querySelectorAll(".question-content .question .delete-container");
   const questionDeleteBtnAll = document.querySelectorAll(".question-delete-btn");
   questionUpdateBtnAll.forEach(function (updateBtn, idx) {
      let questionLinkTitle = questionLinkTitleAll[idx];
      let questionDiv = questionContentQuestionAll[idx];
      let questionInner = questionContentQuestionInnerAll[idx];
      let questionContent = questionContentInnerContentAll[idx];
      let questionDeleteContainer = questionDeleteContainerAll[idx];
      let questionDeleteBtn = questionDeleteBtnAll[idx];
      updateBtn.addEventListener("click", function (e) {
         let question_id = e.target.getAttribute("data-id");
         let question_secret = e.target.getAttribute("data-secret");
         let question_type = e.target.getAttribute("data-type");
         let question_title = e.target.getAttribute("data-title");

         dropZoneRelatedReset();
         QnaRelatedReset();

         updateBtn.style.display = "none";
         questionLinkTitle.style.display = "none";
         questionInner.style.display = "none";
         questionDeleteContainer.style.display = "block";
         questionDiv.insertAdjacentHTML("afterbegin", questionHtml);
         /*SimpleSunEditor 생성 ################################*/
         SimpleSunEditor = SUNEDITOR.create('editorHiddenText',
             Object.assign({}, simpleSunEditorBaseSet, simpleSunEditorButton));

         SunEditorUtils.disableImageUpload(SimpleSunEditor);

         let questionIdInputTag = document.querySelector("#question_id");
         let questionSecretInputTag = document.querySelector("#is_secret");
         let questionTypeSelectTag = document.querySelector("#question_type");
         let questionTitleInputTag = document.querySelector("#question_title");
         questionIdInputTag.value = question_id;
         if (question_secret === "True") {
            questionSecretInputTag.checked = true;
         }
         questionTypeSelectTag.value = question_type;
         questionTitleInputTag.value = question_title;

         const questionCancelBtn = document.querySelector(".question-cancel-btn");
         questionCancelBtn.addEventListener("click", function (e) {
            const existingQuestionForm = document.querySelector(".question-form");
            if (existingQuestionForm) {
               existingQuestionForm.remove();
            }
            updateBtn.style.display = "block";
            questionLinkTitle.style.display = "block";
            questionInner.style.display = "block";
            questionDeleteContainer.style.display = "none";
         }, false);

         questionDeleteBtn.addEventListener("click", function (e){
            let currentPath = document.location.href;
            let targetQuestionId = questionDeleteBtn.getAttribute("data-id");
            let currentUserId = questionDeleteBtn.getAttribute("data-user-id");
            let formData = new FormData();
            formData.append("question_id", targetQuestionId);
            formData.append("current_path", currentPath);
            formData.append("user_id", currentUserId);
            let url = productQuestionDeleteAjax;
            let type = "successRedirect";
            AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, null, type, null);
         },false);

         const submitBtn = document.querySelector("#question-submit");
         const sunEditorForm = document.querySelector(".simpleEditor-form");
         const sunEditorEditable = sunEditorForm.querySelector(".se-container .se-wrapper .sun-editor-editable");
         sunEditorEditable.innerHTML = questionContent.innerHTML;
         submitBtn.addEventListener("click", function (e) {
            document.querySelector("#editorHiddenText").innerHTML = sunEditorEditable.innerHTML;
         }, false);

      }, false);
   });

   /*질문제목 클릭 ===> 내용열기*/
   const questionLinkBtnAll = document.querySelectorAll(".question-link");
   const questionContentAll = document.querySelectorAll(".question-content");
   questionLinkBtnAll.forEach(function (linkBtn, idx) {
      let questionContent = questionContentAll[idx];
      linkBtn.addEventListener("click", function (e) {
         e.preventDefault();

         questionContentAll.forEach(function (queContent) {
            if (queContent.classList.contains("open") && queContent !== questionContent) {
               queContent.classList.remove("open");
            }
         });

         dropZoneRelatedReset();
         QnaRelatedReset();

         questionContent.classList.toggle("open");
      }, false);
   });

   if (typeof productQuestionReplySave !== "undefined") { /*답변하는 admin or staff 를 가려내는 분기*/
      const replyHtml = `<div class="reply-form mt-10">
                            <form action=${productQuestionReplySave} method="POST" enctype="multipart/form-data">
                                <div class="editor-container">
                                   <div class="simpleEditor-form">
                                        <div class="simpleEditor-container">
                                            <textarea id="editorHiddenText" name="content" style="display: none"></textarea>
                                        </div>
                                 </div>
                               </div>
                               <div class="btn-container">
                                   <input type="hidden" id="reply_user_id" name="user_id" value="${currentUserId}">
                                   <input type="hidden" id="reply_product_id" name="product_id" value="${targetProductId}">
                                   <input type="hidden" id="reply_question_id" name="question_id" value="">
                                   <input type="hidden" id="reply_id" name="reply_id" value="">
                                   <input type="hidden" name="csrf_token" value="${CSRF_TOKEN}">
                                   <input type="hidden" id="current_path" name="current_path" value="${currentFullPath}">
                                   <button class="reply-cancel-btn uk-button uk-button-default" type="button" uk-tooltip="title: 작성취소; pos: bottom">
                                        <i class="fas fa-sync-alt"><!--작성 취소--></i>
                                    </button>
                                   <button class="uk-button uk-button-default" type="submit" id="reply-submit" uk-tooltip="title: 저장; pos: bottom">
                                        <i class="fas fa-save"><!--저장--></i>
                                   </button>
                               </div>
                           </form>
                       </div>`;
      /*Reply Create*/
      const replyFormAll = document.querySelectorAll(".reply-form-container");
      replyBtnAll.forEach(function (replyBtn, idx) {
         let replyForm = replyFormAll[idx];
         replyBtn.addEventListener("click", function (e) {
            e.preventDefault();

            dropZoneRelatedReset();
            QnaRelatedReset();

            let question_id = e.target.getAttribute("data-id");
            replyBtn.style.display = "none";
            replyForm.style.display = "block";
            replyForm.insertAdjacentHTML("afterbegin", replyHtml);
            /*SimpleSunEditor 생성 ################################*/
            SimpleSunEditor = SUNEDITOR.create('editorHiddenText',
                Object.assign({}, simpleSunEditorBaseSet, simpleSunEditorButton));

            SunEditorUtils.disableImageUpload(SimpleSunEditor);

            let questionIdInputTag = document.querySelector("#reply_question_id");
            questionIdInputTag.value = question_id;

            const replyCancelBtn = document.querySelector(".reply-cancel-btn");
            replyCancelBtn.addEventListener("click", function (e) {
               const existingReplyForm = document.querySelector(".reply-form");
               if (existingReplyForm) {
                  existingReplyForm.remove();
               }
               replyBtn.style.display = "block";
            }, false);

            const submitBtn = document.querySelector("#reply-submit");
            const sunEditorForm = document.querySelector(".simpleEditor-form");
            const sunEditorEditable = sunEditorForm.querySelector(".se-container .se-wrapper .sun-editor-editable");
            submitBtn.addEventListener("click", function (e) {
               document.querySelector("#editorHiddenText").innerHTML = sunEditorEditable.innerHTML;
            }, false);


         }, false);
      });

      /*Reply Update*/
      const questionContentReplyAll = document.querySelectorAll(".question-content .reply");
      const questionContentReplyInnerAll = document.querySelectorAll(".question-content .reply .inner");
      const questionContentReplyInnerContentAll = document.querySelectorAll(".question-content .reply .inner .content");
      replyUpdateBtnAll.forEach(function (reUpBtn, idx) {
         let replyDiv = questionContentReplyAll[idx];
         let replyInner = questionContentReplyInnerAll[idx];
         let replyContent = questionContentReplyInnerContentAll[idx];
         reUpBtn.addEventListener("click", function (e) {
            e.preventDefault();

            dropZoneRelatedReset();
            QnaRelatedReset();

            let reply_id = e.target.getAttribute("data-id");
            let question_id = e.target.getAttribute("data-question-id");
            reUpBtn.style.display = "none";
            replyInner.style.display = "none";
            replyDiv.insertAdjacentHTML("afterbegin", replyHtml);
            /*SimpleSunEditor 생성 ################################*/
            SimpleSunEditor = SUNEDITOR.create('editorHiddenText',
                Object.assign({}, simpleSunEditorBaseSet, simpleSunEditorButton));

            SunEditorUtils.disableImageUpload(SimpleSunEditor);

            let questionIdInputTag = document.querySelector("#reply_question_id");
            let replyIdInputTag = document.querySelector("#reply_id");
            questionIdInputTag.value = question_id;
            replyIdInputTag.value = reply_id;

            const replyCancelBtn = document.querySelector(".reply-cancel-btn");
            replyCancelBtn.addEventListener("click", function (e) {
               const existingReplyForm = document.querySelector(".reply-form");
               if (existingReplyForm) {
                  existingReplyForm.remove();
               }
               reUpBtn.style.display = "block";
               replyInner.style.display = "block";
            }, false);

            const submitBtn = document.querySelector("#reply-submit");
            const sunEditorForm = document.querySelector(".simpleEditor-form");
            const sunEditorEditable = sunEditorForm.querySelector(".se-container .se-wrapper .sun-editor-editable");
            sunEditorEditable.innerHTML = replyContent.innerHTML;
            submitBtn.addEventListener("click", function (e) {
               document.querySelector("#editorHiddenText").innerHTML = sunEditorEditable.innerHTML;
            }, false);

         }, false);
      });
   }

   function questionContentReset() {
      questionContentAll.forEach(function (queContent) {
         if (queContent.classList.contains("open")) {
            queContent.classList.remove("open");
         }
      });
   }

   /*행여라도, 답변 폼등이 열려 있으면 닫아준다.(관리자나 스태프만 답변을 달기 때문에 열려 있을리 없지만....)*/
   function QnaRelatedReset() {
      questionDeleteContainerAll.forEach(function (questionDeleteContainer){
      if (questionDeleteContainer.style.display === "block") {
         questionDeleteContainer.style.display = "none";
      }
      });

      const existingQuestionForm = document.querySelector(".question-form");
      if (existingQuestionForm) {
         existingQuestionForm.remove();
      }
      if (questionBtn) {
         if (questionBtn.style.display === "none") {
            questionBtn.style.display = "block";
         }
      }

      const existingReplyForm = document.querySelector(".reply-form");
      if (existingReplyForm) {
         existingReplyForm.remove();
      }
      replyBtnAll.forEach(function (reBtn) {
         if (reBtn.style.display === "none") {
            reBtn.style.display = "block";
         }
      });
      replyUpdateBtnAll.forEach(function (reUpBtn) {
         if (reUpBtn.style.display === "none") {
            reUpBtn.style.display = "block";
         }
      });

      questionLinkTitleAll.forEach(function (linkTitle) {
         if (linkTitle.style.display === "none") {
            linkTitle.style.display = "block";
         }
      });
      questionContentQuestionInnerAll.forEach(function (contentInner) {
         if (contentInner.style.display === "none") {
            contentInner.style.display = "block";
         }
      });
      questionUpdateBtnAll.forEach(function (upBtn) {
         if (upBtn.style.display === "none") {
            upBtn.style.display = "block";
         }
      });
      const questionContentReplyInnerAll = document.querySelectorAll(".question-content .reply .inner");
      questionContentReplyInnerAll.forEach(function (replyInner) {
         if (replyInner.style.display === "none") {
            replyInner.style.display = "block";
         }
      });
      replyUpdateBtnAll.forEach(function (reUpBtn) {
         if (reUpBtn.style.display === "none") {
            reUpBtn.style.display = "block";
         }
      });

   }



});