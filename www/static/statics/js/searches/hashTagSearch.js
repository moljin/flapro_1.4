 "use strict"
 /*jshint esversion: 6 */

document.addEventListener('DOMContentLoaded', function () {

    document.addEventListener("click", function (e){
        let target = e.target;
        if (target.classList.contains("hashTag")) {
            let hashTag = target.innerHTML.split("#")[1].split(",")[0];

            if (typeof acDetail !== 'undefined') {
                let _url = acDetail;
                AjaxUtils.hashTagSearch(_url, hashTag);
            }

            console.log("else");

        }
    }, false);

});