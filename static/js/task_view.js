/**
 * Author: Ying Lin
 * Date: Sep 30, 2018
 */
var _identifier = decodeURIComponent(window.location.pathname.substring(6));
console.log(_identifier);

$(document).ready(function () {
    retrieve_subtasks();
    retrieve_config();
    retrieve_result();
})
    .on('click', '#tv-delete-task-button', delete_button_click)
;

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
    $('ul#tv-result-list').prepend(li);
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
            var primitive_vals = [];
            $.each(result, function (rst_key, rst) {
                var rst_type = rst.type;
                var rst_val = rst.value;

                switch (rst_type) {
                    case 'table':
                        _handle_table_result(rst_key, rst_val);
                        break;
                    case 'int': case 'float': case 'str': case 'file': case 'list':
                        primitive_vals.push({key: rst_key, value: rst_val, type: rst_type});
                        break;
                    default:
                        break;
                }
            });
            _handle_primitive_result(primitive_vals);
        }
    });
}

function _handle_primitive_config(key, value) {
    var tr = $('<tr></tr>');
    tr.append($('<td width="150"></td>').text(key));
    tr.append($('<td></td>').text(value).addClass('monospace'));
    $('#tv-config-table').append(tr);
}

function _handle_json_config(key, value) {
    var tr = $('<tr></tr>');
    tr.append($('<td width="150"></td>').text(key));
    tr.append($('<td></td>').html("<pre>" + JSON.stringify(value, undefined, 4) + "</pre>"));
    $('#tv-config-table').append(tr);
}

function retrieve_config() {
    $.post({
        'url': '/api/get_task_configs',
        'data': {identifier: _identifier},
        'success': function (data) {
            var config = data.data;
            $.each(config, function (conf_key, conf) {
                var conf_type = conf.type;
                var conf_val = conf.value;
                switch (conf_type) {
                    case 'int': case 'float': case 'str': case 'file':
                        _handle_primitive_config(conf_key, conf_val);
                        break;
                    case 'json':
                        _handle_json_config(conf_key, conf_val);
                        break;
                }
            })
        }
    });
}

function retrieve_subtasks() {
    var subtask_list = $('ul#tv-subtasks-list');
    $.post({
        'url': '/api/list_children',
        'data': {parent: _identifier, info: true},
        'success': function (data) {
            var subtasks = data.data;
            $.each(subtasks, function (i, subtask) {
                var name = subtask.name;
                var status = subtask.status;
                var id = subtask.identifier;
                var desc = subtask.desc;
                var task_li = $('<li></li>')
                    .addClass('tv-subtasks-item')
                    .attr('status', status);
                task_li.append($('<a class="tv-subtasks-name"></a>')
                    .text(name)
                    .attr('identifier', id)
                    .attr('href', '/task/' + id)
                    .attr('target', '_blank')
                );
                task_li.append($('<span class="tv-subtasks-desc"></span>')
                    .text(desc)
                );
                subtask_list.append(task_li);
            })
        }
    });
}

function delete_button_click() {
    popup(
        'Are you sure you want to delete this task? The operation can not be undone.',
        function () {
            $.post({
                url: '/api/delete_task',
                data: {identifier: _identifier},
                success: function () {
                    window.location.replace('/projects');
                }
            });
            return false;
        }
    )
}