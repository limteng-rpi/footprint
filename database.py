import os
import json
import time
import shutil

root = os.path.dirname(os.path.abspath(__file__))
db_dir_path = os.path.join(root, 'database')
db_json_path = os.path.join(db_dir_path, 'database.json')
proj_dir_path = os.path.join(db_dir_path, 'projects')


def append_database_json_val(k: str, v: str) -> bool:
    """
    :param k: Property key.
    :param v: Value to append.
    :return:
    """
    try:
        db_json = json.load(open(db_json_path, 'r', encoding='utf-8'))
        if k in db_json:
            if v not in db_json[k]:
                db_json[k].append(v)
        else:
            db_json[k] = [v]
        json.dump(db_json, open(db_json_path, 'w', encoding='utf-8'))
        return True
    except:
        return False


def remove_database_json_val(k: str, v: str) -> bool:
    """
    :param k: Property key.
    :param v: Value to remove.
    :return:
    """
    try:
        db_json = json.load(open(db_json_path, 'r', encoding='utf-8'))
        if k in db_json and v in db_json[k]:
            db_json[k].remove(v)
            json.dump(db_json, open(db_json_path, 'w', encoding='utf-8'))
            return True
    except:
        return False
    return False


def project_exist(name: str) -> bool:
    """Check if a project exists by name.
    :param name: Project name.
    :return:
    """
    proj_path = os.path.join(db_dir_path, 'projects', name)
    return (os.path.exists(proj_path) and os.path.isdir(proj_path))


def create_project(name: str, desc: str = '') -> (bool, str):
    """Create a project.

    :param name: Project name.
    :param desc: Description.
    :return:
    """
    create_time = int(time.time())

    if project_exist(name):
        return False, 'Project exists'
    else:
        try:
            # Create project directory
            proj_path = os.path.join(proj_dir_path, name)
            os.makedirs(proj_path)
            # Create properties.json
            json.dump({'name': name,
                       'description': desc,
                       'tasks': [],
                       'create': create_time
            }, open(os.path.join(proj_path, 'properties.json'),
                    'w', encoding='utf-8'))
            # Add to database.json
            append_database_json_val('projects', name)
            return True,
        except Exception as e:
            return False, str(e)


def delete_project(name) -> (bool, str):
    """Delete a project by name.
    :param name: Project name.
    :return:
    """
    if project_exist(name):
        try:
            shutil.rmtree(os.path.join(proj_dir_path, name))
            return True,
        except:
            return False, 'Failed to delete the project directory'
    else:
        return False, 'Project doesn\'t exist'