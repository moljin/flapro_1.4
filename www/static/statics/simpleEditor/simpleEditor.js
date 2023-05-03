"use strict";
/*jshint esversion: 6 */

document.addEventListener('DOMContentLoaded', function () {
    const simpleSunEditorBaseSet = SunEditorUtils.baseSet();
    const simpleSunEditorButton = SunEditorUtils.simpleButton();

    let SunEditor;
    SunEditor = SUNEDITOR.create('editorHiddenText',
        Object.assign({}, simpleSunEditorBaseSet, simpleSunEditorButton));



});