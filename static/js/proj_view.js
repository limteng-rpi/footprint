/**
 * Author: Ying Lin
 * Date: Sep 30, 2018
 */

$(document).ready(function () {
    retrieve_project_list();
});

function update_project_list(projs) {
    var proj_list = $('#proj-list');
    proj_list.empty();
    $.each(projs, function (i, proj) {
        console.log(proj)
        var name = proj.name;
        var identifier = proj.identifier;
        var task_num = (typeof proj.tasks === 'undefined')? 0 : proj.tasks.length;
        var run_num = 0;
        var fail_num = 0;
        var done_num = 0;
        if (task_num > 0) {
            $.each(proj.tasks, function (ti, task) {
                switch (task.status) {
                    case 'running':
                        run_num += 1;
                        break;
                    case 'failed':
                        fail_num += 1;
                        break;
                    case 'done':
                        done_num += 1;
                        break;
                    default:
                        break;
                }
            });
        }

        var proj_li = $('<li></li>').addClass('proj-li');
        // Project information
        var proj_info = $('<div></div>').addClass('proj-info');
        var proj_summary = $('<div></div>').addClass('proj-summary');
        proj_summary.append($('<span class="proj-s-name ellipsis"></span>').text(name));
        proj_summary.append($('<span class="proj-s-task"></span>').text('Task: ' + task_num));
        proj_summary.append($('<span class="proj-s-run"></span>').html('<i class="fas fa-circle fa-sm"></i> Running: ' + run_num));
        proj_summary.append($('<span class="proj-s-fail"></span>').html('<i class="fas fa-circle fa-sm"></i> Failed: ' + fail_num));
        proj_summary.append($('<span class="proj-s-done"></span>').html('<i class="fas fa-circle fa-sm"></i> Done: ' + done_num));

        var proj_ops = $('<div></div>').addClass('proj_ops');
        var proj_arch_btn = $('<button class="trans gray"><i class="far fa-eye-slash"></i> Archive</button>');
        proj_ops.append(proj_arch_btn);

        proj_info.append(proj_summary, proj_ops);

        // Project tasks
        var proj_tasks = $('<div></div>').addClass('proj-tasks');
        var proj_tasks_ops = $('<div></div>').addClass('proj-tasks-ops');
        var proj_tasks_ops_left = $('<div></div>').addClass('proj-tasks-ops-left');
        var new_task_btn = $('<button class="outline"><i class="fas fa-plus"></i> New Task</button>')
            .attr('proj', identifier);
        proj_tasks_ops_left.append(new_task_btn);
        var proj_tasks_ops_right = $('<div></div>').addClass('proj-tasks-ops-right');
        var del_proj_btn = $('<button class="outline red"><i class="fas fa-trash"></i> Delete Project</button>')
            .attr('proj', identifier);
        proj_tasks_ops_right.append(del_proj_btn);
        proj_tasks_ops.append(proj_tasks_ops_left, proj_tasks_ops_right);

        var proj_tasks_list = $('<ul></ul>').addClass('proj-tasks-list').attr('proj', identifier);
        $.each(proj.tasks, function (ti, task) {
            var task_li = $('<li></li>')
                .addClass('proj-tasks-item')
                .attr('status', task.status);
            task_li.append($('<a class="proj-tasks-name"></a>')
                .text(task.name)
                .attr('identifier', task.identifier)
                .attr('href', '/task/' + task.identifier)
                .attr('target', '_blank')
            );
            proj_tasks_list.append(task_li);
        });
        proj_tasks.append(proj_tasks_ops, proj_tasks_list);

        proj_li.append(proj_info, proj_tasks);
        proj_list.append(proj_li);
    })
}

function retrieve_project_list() {
    $.post({
        'url': '/api/list_projects',
        'data': {info: true},
        'success': function (data) {
            update_project_list(data.data);
        }
    });
}
