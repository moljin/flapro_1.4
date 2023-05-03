"use strict";
/*jshint esversion: 6 */

// Javascript 브라우저 Resize 이벤트 최적화 하기 https://inpa.tistory.com/entry/jQuery-%F0%9F%93%9A-%EB%B8%8C%EB%9D%BC%EC%9A%B0%EC%A0%80-resize-%EC%9D%B4%EB%B2%A4%ED%8A%B8-%EC%82%AC%EC%9A%A9%EB%B2%95-%EC%B5%9C%EC%A0%81%ED%99%94

let delay = 300;
let timer = null;

window.addEventListener('resize', function(){
	clearTimeout(timer);
	timer = setTimeout(function(){
		console.log('resize event!');

        if (window.innerWidth <= 800) {
      		// alert('현재 브라우저 크기가 <= 800px')
            console.log("'현재 브라우저 크기가 <= 800px'")
   		}
	}, delay);
});

/*
window.onload = function () {
    const sunEditable = document.querySelector(".sun-editor-editable");
    videoResize(sunEditable);
    window.addEventListener('resize', function(){
        videoResize(sunEditable);
    });
};

function videoResize(sunEditable){
	    const seVideoContainerAll = sunEditable.querySelectorAll(".se-video-container");
        const seVideoContainerFigureAll = sunEditable.querySelectorAll(".se-video-container figure");
        seVideoContainerFigureAll.forEach(function (figure, idx) {
            seVideoContainerAll.forEach(function (container, idx) {
                if (figure.offsetWidth + 2 === container.offsetWidth) {
                    let iframe = figure.querySelector("iframe");
                    let object = figure.querySelector("object");
                    let embed = figure.querySelector("embed ");
                    figure.style.cssText = ` position: relative;
                                            padding-bottom: 56.25%;
                                            padding-top: 30px; 
                                            height: 0; 
                                            overflow: hidden;
                                            `;
                    iframe.style.cssText = ` position: absolute;
                                            top: 0;
                                            left: 0;
                                            width: 100%!important;
                                            height: 100%!important;
                                            `;
                }
            });
        });
}
*/