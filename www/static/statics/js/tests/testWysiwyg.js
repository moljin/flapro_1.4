 "use strict"
 /*jshint esversion: 6 */

document.addEventListener('DOMContentLoaded', function () {
    let isFocus = false;
    const SimpleEditor = document.querySelector(".contentEditable");
    const hiddenTextarea = document.querySelector("#hiddenTextarea");

    const bold = document.querySelector(".bold");
    const italic = document.querySelector(".italic");
    const underline = document.querySelector(".underline");
    const alignJustify = document.querySelector(".align-justify");
    const alignLeft = document.querySelector(".align-left");
    const alignCenter = document.querySelector(".align-center");
    const alignRight = document.querySelector(".align-right");
    const ulList = document.querySelector(".ul-list");
    const olList = document.querySelector(".ol-list");

    SimpleEditor.addEventListener("keyup", cloneContent);
    SimpleEditor.addEventListener('focus',function (e){isFocus = true;},false);
    SimpleEditor.addEventListener('focusout',function (e){isFocus = false;},false);

    bold.addEventListener("click", function (e){document.execCommand('bold');});
    italic.addEventListener("click", function (e){document.execCommand('italic');});
    underline.addEventListener("click", function (e){document.execCommand('underline');});
    alignJustify.addEventListener("click", function (e){document.execCommand('justifyFull');});
    alignLeft.addEventListener("click", function (e){document.execCommand('justifyLeft');});
    alignCenter.addEventListener("click", function (e){document.execCommand('justifyCenter');});
    alignRight.addEventListener("click", function (e){document.execCommand('justifyRight');});
    ulList.addEventListener("click", function (e){document.execCommand('insertUnorderedList');});
    olList.addEventListener("click", function (e){document.execCommand('insertOrderedList');});

    function cloneContent(){
        hiddenTextarea.value = SimpleEditor.innerHTML;
    }

});