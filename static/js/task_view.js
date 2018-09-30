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
            console.log(config);
        }
    })
}

function _handle_table_result(key, val) {
    var table = $('<li class="tv-result-li"><table></table></li>');
    var thead = $('<thead><tr></tr></thead>');
    $.each(val.cols, function (i, col) {
        thead.append($('<td></td>').text(col));
    });
    var tbody = $('<tbody></tbody>');
    $.each(val.data, function (i, row) {
        var tr = $('<tr></tr>');
        $.each(row, function (j, v) {
            if (typeof v === 'number' && !Number.isInteger(v)) {
                v = Number.parseFloat(v).toPrecision(2);
            }
            tr.append($('<td></td>').text(v));
        });
    });

    table.append(thead, tbody);
    $('ul#tv-result-list').append(table);
}

function retrieve_result() {
    $.post({
        'url': '/api/get_task_results',
        'data': {identifier: _identifier},
        'success': function (data) {
            var result = data.data;
            console.log(result);
            $.each(result, function (rst_key, rst) {
                var rst_type = rst.type;
                var rst_val = rst.value;

                switch (rst_type) {
                    case 'table':
                        _handle_table_result(rst_key, rst_val);
                        break;
                    default:
                        break;
                }
            });
        }
    });
}