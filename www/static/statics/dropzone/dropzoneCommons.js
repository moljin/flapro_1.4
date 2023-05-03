"use strict"
/*jshint esversion: 6 */

let dropzoneSet;
let module21Utils;

(function(window){
    let dropzoneSetting = {
        dzBaseSet: function (_url, removeBtn) {
            return {
                url: _url,
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
        },
        dzSendingFunc: function (dropZone, currentPath, boardIdInputTag) {
            dropZone.on("sending", function (file, xhr, formData) {
            dropzoneSet.dzFormData(formData, currentPath, boardIdInputTag);
         });
        },
        dzFormData: function (formData, currentPath, boardIdInputTag) {
            formData.append("current_path", currentPath);
            formData.append("review_id", boardIdInputTag.value);
            formData.append("user_id", document.querySelector("#user_id").value);
            formData.append("product_id", document.querySelector("#product_id").value);
            // formData.append("content", document.querySelector("#content-textarea").value);
            formData.append("content", document.querySelector("#editorHiddenText").value);
        },
        dzFuncSet: function (dropZone, addedFiles, successCount) {
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

            dropZone.on("success", function (file, response, progressEvent) {
                if (file.accepted) {
                    successCount++;
                }

                if (dropZone.files.length === successCount) {
                    console.log(successCount);
                }
                window.location.assign(response.redirect_url);
                window.location.reload();
            });

            dropZone.on("error", function (file, res_html) {
                const errorMessageTagList = document.querySelectorAll(".dz-error-message span");
                errorMessageTagList.forEach(function (messageTag, idx) {
                    messageTag.innerHTML = "업로드가 완료되지 않았어요!!";
                });
                console.log("error", file);
                // console.log(res_html)
            });

            dropZone.on("processingmultiple", function (fileList) {
                console.log("processingmultiple", fileList);
            });

            dropZone.on("sendingmultiple", function (fileList) {
                console.log("sendingmultiple", fileList);
            });
        },

    };

    let module21 = {
        test2Func: function (param) {
            console.log(param);
            alert('module2 in CommonUtils');
        },
        getInteger: function (num) {
            return num;
        },
    };

    dropzoneSet = dropzoneSetting;
    module21Utils = module21;
}(window));
