"use strict"
/*jshint esversion: 6 */
toTopPaginationInit();
/*페이지 클릭시 toTopPaginate*/
function toTopPaginationInit() {
    let loadPath = window.location.href;

    let topPageObj = document.querySelector("#top_page_obj");
    let topPageObj_2 = document.querySelector("#top_page_obj_2");

    if (topPageObj) {
        if (loadPath.includes("&page=") &&
            (loadPath.split("&page_2=")[1].includes("&page=")) &&
            !loadPath.includes("#" + topPageObj.value)) {
            window.location.href = loadPath + "#" + topPageObj.value;
        }
    }

    if (topPageObj_2) {
        if (loadPath.includes("&page_2=") &&
            (loadPath.split("&page=")[1].includes("&page_2=")) &&
            !loadPath.includes("#" + topPageObj_2.value)) {
            window.location.href = loadPath + "#" + topPageObj_2.value;
        }
    }









}