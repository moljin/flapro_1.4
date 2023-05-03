 "use strict"
 /*jshint esversion: 6 */

document.addEventListener('DOMContentLoaded', function () {

    const pageLinks = document.getElementsByClassName("page-link");
    Array.from(pageLinks).forEach(function (link) {
        link.addEventListener('click', function () {
            document.getElementById('page').value = this.dataset.page;
            document.getElementById('searchForm').submit();
        });
    });

    const btnSearch = document.getElementById("btn_search");
    btnSearch.addEventListener('click', function () {
        document.getElementById('kw').value = document.getElementById('search_kw').value;
        document.getElementById('page').value = 1;  // 검색버튼을 클릭할 경우 1페이지부터 조회한다.
        document.getElementById('searchForm').submit();
    });

});