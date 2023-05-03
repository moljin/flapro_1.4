"use strict"
/*jshint esversion: 6 */
profilesInit();

function profilesInit() {
    let _width = ``;
    let _height = ``;
    try { // Single cover image
        const coverImgInput = document.querySelector("#cover-image");
        const coverImgPreviewTag = document.querySelector('#cover-img-preview');
        const existingCoverImagePath = document.getElementById("cover-img-preview").getAttribute("src");
        ImageUtils.eachImagePreview(_width, _height, coverImgInput, coverImgPreviewTag, existingCoverImagePath, null, null);
    } catch (e) {
        console.log("");
    }

    try { // profile image
        const profileImgInput = document.querySelector("#profile-image");
        const profileImgPreviewTag = document.querySelector('#profile-img-preview');
        const existingProfileImagePath = document.getElementById("profile-img-preview").getAttribute("src");
        ImageUtils.eachImagePreview(_width, _height, profileImgInput, profileImgPreviewTag, existingProfileImagePath, null, null);
    } catch (e) {
        console.log("");
    }

    try { // business license
        const corpImgInput = document.querySelector("#corp-image");
        const corpImgPreviewTag = document.querySelector('#corp-img-preview');
        const existingCorpImagePath = document.getElementById("corp-img-preview").getAttribute("src");
        ImageUtils.eachImagePreview(_width, _height, corpImgInput, corpImgPreviewTag, existingCorpImagePath, null, null);
    } catch (e) {
        console.log("", e);
    }

    /*#################################### user ####################################*/
    // admin/user nickname name check
    // corp_brand name check 는 vendor.js 에 ...
    const nicknameCheckBtn = document.querySelector("#nickname-check-btn");
    if (nicknameCheckBtn) {
        nicknameCheckBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const flashAlert_div = document.querySelector(".profile-update-alert");
            let nickname = document.querySelector("#nickname").value;
            let profile_id = document.querySelector("#profile_id").value;
            let user_id = document.querySelector("#user_id").value;
            let user_email;
            if (document.querySelector("[name='user_email']")) {
                user_email = document.querySelector("[name='user_email']").value;
            } else {
                user_email = "";
            }
            console.log(user_email)
            let formData = new FormData();
            formData.append("nickname", nickname);
            formData.append("profile_id", profile_id);
            formData.append("user_id", user_id);
            formData.append("user_email", user_email);
            let url = existingNicknameCheckAjax;
            let type = "onlyFlashMessageOrWindowReload";
            AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, flashAlert_div, type, null);
        }, false);
    }

    const profileAlert = document.querySelector(".profile-update-alert");
    const profileDetailAlert = document.querySelector(".profile-detail-alert");
    const profileSaveBtn = document.querySelector("#profile-save-btn");
    const coverImgTag = document.querySelector("#cover-path");
    const profileImgTag = document.querySelector("#profile-path");
    const globalProfileImgTag = document.querySelector("#global-profile-img");
    const nicknameSpanTag = document.querySelector(".profile > .upper > span.nickname");
    const messageDivTag = document.querySelector(".profile > .lower > div.message");
    if (profileSaveBtn) {
        profileSaveBtn.addEventListener("click", function (e) {
            e.preventDefault();
            let _id = document.querySelector("#user_id").value;
            let nickname = document.querySelector("#nickname").value;
            let message = document.querySelector("#message").value;
            let profileImage = document.querySelector("#profile-image").files[0];
            let coverImage = document.querySelector("#cover-image").files[0];
            let formData = new FormData();
            formData.append("user_id", _id);
            formData.append("nickname", nickname);
            formData.append("message", message);
            formData.append("profile_image", profileImage);
            formData.append("cover_image", coverImage);
            let request = $.ajax({
                url: profileSaveAjax,
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
                        if (response.flash_message) {
                            AlertUtils.alertDisplay(profileAlert, response.flash_message);
                        }
                        if (response._save) {
                            AlertUtils.alertRemove(profileAlert);
                            if (response.cover_img_path) {
                                coverImgTag.setAttribute("src", "/" + response.cover_img_path);
                            }
                            if (response.profile_img_path) {
                                profileImgTag.setAttribute("src", "/" + response.profile_img_path);
                                globalProfileImgTag.setAttribute("src", "/" + response.profile_img_path);
                            }
                            nicknameSpanTag.innerHTML = response.nickname;
                            messageDivTag.innerHTML = response._message;
                            if (response._save === "create") {
                                let deleteModalLink = `<a href="#profile-delete-modal" uk-toggle><span uk-icon="trash"></span></a>`;
                                let deleteModal = `<div id="profile-delete-modal" class="uk-flex-top" uk-modal>
                                                        <div class="uk-modal-dialog uk-modal-body uk-margin-auto-vertical">
                                                            <button class="uk-modal-close-default" type="button" uk-close></button>
                                                            정말로 프로필을 삭제하시겠어요?
                                                            <div class="btn uk-inline ml-15">
                                                                <input type="hidden" id="profile-id" value="` + response.profile_id + `">
                                                                <button class="uk-button uk-button-primary uk-modal-close" type="button">삭제</button>
                                                            </div>
                                                        </div>
                                                    </div>`;
                                document.querySelector(".profile .upper").insertAdjacentHTML("beforeend", deleteModalLink);
                                document.querySelector(".content .profile").insertAdjacentHTML("beforeend", deleteModal);

                                const profileDeleteBtn = document.querySelector("#profile-delete-modal .btn");
                                profileDeleteBtn.addEventListener("click", function (e) {
                                    e.preventDefault();
                                    const profileId = document.querySelector("#profile-id").value;
                                    profilesDelete(profileId, profileDetailAlert);
                                }, false);
                            }
                            document.querySelector("#profile-save-modal").style.display = "none";
                            window.location.reload(); // 모두 ajax 로 채워넣고 reload
                        }
                        if (response._err && response.res_msg) {
                            window.location.href = response.redirect_url + '?res_msg=' + response.res_msg;
                        }

                    }
                },
                error: function (err) {
                    AjaxUtils.serverErrorAlert(err);
                }
            });
        }, false);
    }


    // admin/user profile detail delete
    // 선택자를 user 와는 다르게 잡았다.
    const profileDeleteBtn = document.querySelector("#profile-delete-btn");
    if (profileDeleteBtn) {
        profileDeleteBtn.addEventListener('click', function (e) {
            e.preventDefault();
            let profileId = document.querySelector("#profile_id").value;
            profilesDelete(profileId);

        }, false);
    }

    /*#################################### admin ####################################*/
    //admin profiles list check delete
    othersScript.checkBoxCheck();

    const checkedDeleteBtn = document.querySelector("#checked-delete-btn");
    const checkBoxList = document.querySelectorAll("input.single");
    if (checkedDeleteBtn) {
        checkedDeleteBtn.addEventListener("click", function (e) {
            e.preventDefault();
            Array.from(checkBoxList).forEach(function (checkBox) {
                if (checkBox.checked) {
                    let _id = Number(checkBox.getAttribute("id"));
                    profilesDelete(_id);
                }
            });

        });
    }

}

function profilesDelete(_id) {
    let url = profileDeleteAjax;
    let formData = new FormData();
    formData.append("profile_id", _id);
    let type = "successRedirect";
    AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, null, type, null);
}
