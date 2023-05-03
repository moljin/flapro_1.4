"use strict"
/*jshint esversion: 6 */
vendorUpdateInit();
function vendorUpdateInit() {
    const corpBrandCheckBtn = document.querySelector("#corp-brand-check-btn");
    if (corpBrandCheckBtn) {
        corpBrandCheckBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const flashAlert_div = document.querySelector(".vendor-update-alert");
            let corp_brand = document.querySelector("#corp_brand").value;
            let user_id = document.querySelector("#user_id").value;
            let profile_id = document.querySelector("#profile_id").value;
            let user_email;
            if (document.querySelector("[name='user_email']")) {
                user_email = document.querySelector("[name='user_email']").value;
            } else {
                user_email = "";
            }
            console.log(user_email);
            let formData = new FormData();
            formData.append("corp_brand", corp_brand);
            formData.append("user_id", user_id);
            formData.append("profile_id", profile_id);
            formData.append("user_email", user_email);
            let url = existingCorpBrandCheckAjax;
            let type = "onlyFlashMessageOrWindowReload";
            AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, flashAlert_div, type, null);
        }, false);
    }

    const vendorUpdateSubmitBtn = document.querySelector("#vendor-update-submit");
    if (vendorUpdateSubmitBtn) {
        vendorUpdateSubmitBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const flashAlert_div = document.querySelector(".vendor-update-alert");
            let corp_brand = document.querySelector("#corp_brand").value;
            let corp_email = document.querySelector("#corp_email").value;
            let corp_number = document.querySelector("#corp_number").value;
            let corp_online_marketing_number = document.querySelector("#corp_online_marketing_number").value;
            let corp_image = document.querySelector("#corp-image").files[0];
            let corp_address = document.querySelector("#corp_address").value;
            let main_phonenumber = document.querySelector("#main_phonenumber").value;
            let main_cellphone = document.querySelector("#main_cellphone").value;
            let profile_level = document.querySelector("#profile_level").value;
            let formData = new FormData();
            formData.append("corp_brand", corp_brand);
            formData.append("corp_email", corp_email);
            formData.append("corp_number", corp_number);
            formData.append("corp_online_marketing_number", corp_online_marketing_number);
            formData.append("corp_image", corp_image);
            formData.append("corp_address", corp_address);
            formData.append("main_phonenumber", main_phonenumber);
            formData.append("main_cellphone", main_cellphone);
            formData.append("level", profile_level);
            let url = vendorUpdateAjax;
            let type = "onlyFlashMessageOrWindowReload";
            AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, flashAlert_div, type, null);
        }, false);
    }

    const vendorDeleteBtn = document.querySelector("#vendor-delete-btn");
    if (vendorDeleteBtn) {
        vendorDeleteBtn.addEventListener('click', function (e) {
            e.preventDefault();
            let formData = {};
            let url = vendorDeleteAjax;
            let type = "onlyFlashMessageOrWindowReload";
            AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, null, type, null);
        }, false);
    }
}









