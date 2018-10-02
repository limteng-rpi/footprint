$(document).ready(function () {

})
    .on('click', '#popup-cancel-btn', popup_cancel_btn_click);

function popup_cancel_btn_click() {
    $('#popup').hide();
    $('#popup-text').text('');
    $('#popup-confirm-btn').unbind();
}

// TODO: add popup options
function popup(text, confirm_func) {
    $('#popup-text').text(text);
    $('#popup').show();
    $('#popup-confirm-btn').click(function () {
        confirm_func();
        popup_cancel_btn_click();
        return false;
    });
}