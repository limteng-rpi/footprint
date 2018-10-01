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
    var li = $('<li class="tv-result-li"></li>');
    var table_cap = $('<div></div>').addClass('tv-result-cap').text('Table: ' + key);
    var table = $('<table></table>');
    var thead = $('<thead><tr></tr></thead>');
    $.each(val.cols, function (i, col) {
        thead.append($('<th></th>').text(col));
    });
    var tbody = $('<tbody></tbody>');
    $.each(val.data, function (i, row) {
        var tr = $('<tr></tr>');
        $.each(row, function (j, v) {
            if (typeof v === 'number' && !Number.isInteger(v)) {
                v = Number.parseFloat(v).toPrecision(3);
            }
            tr.append($('<td></td>').text(v));
        });
        tbody.append(tr);
    });

    table.append(thead, tbody);
    li.append(table_cap, table);
    $('ul#tv-result-list').append(li);
}

function _handle_primitive_result(rsts) {
    var li = $('<li class="tv-result-li"></li>');
    var table = $('<table></table>');
    var tbody = $('<tbody></tbody>');
    $.each(rsts, function (i, rst) {
        var tr = $('<tr></tr>');
        tr.append($('<td width="200"></td>').text(rst.key).addClass('text-left'));
        switch (rst.type) {
            case 'int': case 'file':
                tr.append($('<td></td>')
                    .text(rst.value)
                    .addClass('monospace')
                    .addClass('text-left')
                );
                break;
            case 'float':
                tr.append($('<td></td>')
                    .text(Number.parseFloat(rst.value).toPrecision(4))
                    .addClass('monospace')
                    .addClass('text-left')
                );
                break;
            case 'list':
                // TODO: implement handler
                break;
            default:
                break;
        }
        tbody.append(tr);
    });
    table.append(tbody);
    li.append(table);
    $('ul#tv-result-list').append(li);
}

function retrieve_result() {
    $.post({
        'url': '/api/get_task_results',
        'data': {identifier: _identifier},
        'success': function (data) {
            var result = data.data;
            // console.log(result);
            var primitive_vals = [];
            $.each(result, function (rst_key, rst) {
                var rst_type = rst.type;
                var rst_val = rst.value;

                switch (rst_type) {
                    case 'table':
                        _handle_table_result(rst_key, rst_val);
                        break;
                    case 'int': case 'float': case 'str': case 'file': case 'list':
                        primitive_vals.push({key: rst_key, value: rst_val, type: rst_type})
                        break;
                    default:
                        break;
                }
            });
            _handle_primitive_result(primitive_vals);
        }
    });
}