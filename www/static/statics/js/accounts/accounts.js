 "use strict"
 /*jshint esversion: 6 */
 accountsDeleteInit();
 function accountsDeleteInit() {
     //registered self delete
     const accountsDeleteBtn = document.querySelector("#accounts-delete-btn");
     if (accountsDeleteBtn) {
         accountsDeleteBtn.addEventListener('click', function (e) {
             e.preventDefault();
             let _id = document.querySelector("#user_id").value;
             accountsDelete(_id);

         }, false);
     }

     //admin user_change delete
     const userDeleteBtn = document.querySelector("#user-delete-btn");
     if (userDeleteBtn) {
         userDeleteBtn.addEventListener('click', function (e) {
             e.preventDefault();
             let _id = document.querySelector("#user_id").value;
             accountsDelete(_id);

         }, false);
     }

     //admin user_list check delete
     othersScript.checkBoxCheck();
     const checkedDeleteBtn = document.querySelector("#checked-delete-btn");
     const checkBoxList = document.querySelectorAll("input.single");
     if (checkedDeleteBtn) {
         checkedDeleteBtn.addEventListener("click", function (e) {
             e.preventDefault();
             Array.from(checkBoxList).forEach(function (checkBox) {
                 if (checkBox.checked) {
                     let _id = Number(checkBox.getAttribute("id"));
                     accountsDelete(_id);
                 }
             });

         });
     }

 }

function accountsDelete (_id) {
    let url = accountsDeleteAjax;
    let formData = new FormData();
    formData.append("_id", _id);
    let type = "successRedirect";
    AjaxUtils.flashMessageRedirectRemoveDiv(url, formData, null, type, null);
}