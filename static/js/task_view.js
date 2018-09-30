/**
 * Author: Ying Lin
 * Date: Sep 30, 2018
 */

var _identifier = decodeURIComponent(window.location.pathname.substring(6));
console.log(_identifier);

$(document).ready(function () {
    retrieve_config();
    retrieve_result();
});

function retrieve_config() {
    $.post({
        'url': '/api/get_task_configs',
        'data': {identifier: _identifier},
        'success': function (data) {
            var config = data.data;
        }
    })
}

function retrieve_result() {
    $.post({
        'url': '/api/get_task_results',
        'data': {identifier: _identifier},
        'success': function (data) {
            var result = data.data;
        }
    })
}