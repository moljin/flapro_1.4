"use strict";
/*jshint esversion: 6 */
// /* jshint expr: true */
let customPlugin = SunEditorUtils.customPlugIn();
let baseSetting = SunEditorUtils.baseSetting();
let generalButtons = SunEditorUtils.generalButtons();
let commentButtons = SunEditorUtils.commentButtons();

const sunInit = document.querySelector("#sun_init").value;
let SunEditor;

/*json 객체 합치기: https://hianna.tistory.com/466*/
/*https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/assign*/
/*product_CU 등도 추가될 예정*/
if (sunInit === "article_CU") {
    SunEditor = SUNEDITOR.create('editorHiddenText',
        Object.assign({}, customPlugin, baseSetting, generalButtons));
} else if (sunInit === "article_comment_CU") { //어드민에서 사용 (cf. 이용자단에서는 따로 commentEditor.js 사용)
    SunEditor = SUNEDITOR.create('editorHiddenText',
        Object.assign({}, customPlugin, baseSetting, commentButtons));
} else if (sunInit === "product_CU") {
    SunEditor = SUNEDITOR.create('editorHiddenText',
        Object.assign({}, customPlugin, baseSetting, generalButtons));
}

SunEditor.onImageUpload = function (targetElement, index, state, imageInfo, remainingFilesCount, core) {
    // let imgSizePercentageBtn = document.querySelector('[data-value="0.75"]');
    let imgSizePercentageBtn = document.querySelector('[data-value="1"]');

    /*이미지를 에디터에 로드할때 이미지 크기 설정 1=100%, 0.75=75%, 0.5=50%*/
    /*아래도 수정*/
    /*imageRoadWithInput.setAttribute("placeholder", "75%");*/

    SunEditorUtils.onImageUploadSize(targetElement, state, core, imgSizePercentageBtn);
};

SunEditor.onVideoUpload = function (targetElement, index, state, info, remainingFilesCount, core) {
    console.log(`targetElement:${targetElement}, index:${index}, state('create', 'update', 'delete'):${state}`);
    console.log(`info:${info}, remainingFilesCount:${remainingFilesCount}`);

    // let videoSizePercentageBtn = document.querySelector('[data-value="0.75"]');
    let videoSizePercentageBtn = document.querySelector('[data-value="1"]');

    /*비디오를 에디터에 로드할때 이미지 크기 설정 1=100%, 0.75=75%, 0.5=50%*/
    /*아래도 수정*/
    /*imageRoadWithInput.setAttribute("placeholder", "75%");*/

    SunEditorUtils.onVideoUploadSize(targetElement, state, core, videoSizePercentageBtn);
};

SunEditor.onload = function (core, reload) {
    const sunSubmit = document.querySelector("#form-submit");
    sunSubmit.addEventListener('click', function () {
        sunEditorImageListSave();
        document.getElementById('editorHiddenText').value = SunEditor.getContents();
    }, false);
};

function sunEditorImageListSave() {
    const sunEditorEditable = document.querySelector(".sun-editor .se-wrapper .sun-editor-editable");
    let imgTagList = sunEditorEditable.querySelectorAll('img');
    imgTagList.forEach(function (imgTag) {
        if (imgTag.getAttribute('src').includes('base64')) {
            const sunInit = document.querySelector("#sun_init").value;
            let ormId = document.querySelector("#orm_id").value;

            let fileName = imgTag.getAttribute('data-file-name');
            let block = imgTag.getAttribute('src').split(';');
            let realData = block[1].split(',')[1]; // 이 경우 '/gj.........Tf/5z0L/2vs1lb4eGcnUco//Z'

            let shopID;
            if (sunInit === "product_CU") {
                shopID = document.querySelector("#shop_id").value;
            }

            let userEmail;
            let articleID;
            let sunImage_init = document.querySelector("#sunImage_init");
            // 이용자단에도 빈값을 가진 태그는 만들어야...,
            // but commentEditor.js 에서는 Editor 붙여넣을때 없어도 됨(이런 구문이 사용되지 않으므로)
            if (sunImage_init.value === "adminArticle_create") {
                userEmail = document.querySelector("[name='user_email']").value;
            } else if (sunImage_init.value === "adminArticle_change") {
                userEmail = document.querySelector("#user_email").value;
            } else if (sunImage_init.value === "adminArticleComment_create") {
                userEmail = document.querySelector("[name='user_email']").value;
                articleID = document.querySelector("[name='article_id']").value;
            } else if (sunImage_init.value === "adminArticleComment_change") {
                userEmail = document.querySelector("#user_email").value;
                articleID = document.querySelector("#article_id").value;
            } else if (sunImage_init.value === "adminProduct_change") {
                userEmail = document.querySelector("#user_email").value;
            }

            let formData = new FormData();
            formData.append('sun_init', sunInit); // 어떤 object 에 해당하는 지 확인하기 위해
            formData.append('orm_id', ormId);
            formData.append('upload_img', realData); // 이미지의 Blob를 폼 데이터 객체에 추가
            formData.append('file_name', fileName);

            if (sunInit === "product_CU") {
                formData.append('shop_id', shopID);
            }

            if (sunImage_init.value === "adminArticle_create") {
                formData.append('user_email', userEmail);
            } else if (sunImage_init.value === "adminArticle_change") {
                formData.append('user_email', userEmail);
            } else if (sunImage_init.value === "adminArticleComment_create") {
                formData.append('user_email', userEmail);
                formData.append('article_id', articleID);
            } else if (sunImage_init.value === "adminArticleComment_change") {
                formData.append('user_email', userEmail);
                formData.append('article_id', articleID);
            } else if (sunImage_init.value === "adminProduct_change") {
                formData.append('user_email', userEmail);
            }
            let url = editorImagesSaveAjax;
            SunEditorUtils.sunImageSave(url, formData, imgTag);
        }

    });
}
// sunEditorCustom
const sunEditorForm = document.querySelector(".suneditor-form");
otherCustomInit();
function otherCustomInit() {
    SunEditorUtils.helpInit(sunEditorForm);
    SunEditorUtils.moreButtonTitleChange(sunEditorForm);
}

sunEditorForm.addEventListener("click", function (e) {
    console.log(e.target);
}, false);

imageVideoRadioButtonInit();
function imageVideoRadioButtonInit() {
    SunEditorUtils.imageVideoRadioButtonInit(sunEditorForm);
    }
