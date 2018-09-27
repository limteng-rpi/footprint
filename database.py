import os
import json
import time
import shutil

root = os.path.dirname(os.path.abspath(__file__))
db_dir_path = os.path.join(root, 'database')
db_json_path = os.path.join(db_dir_path, 'database.json')
proj_dir_path = os.path.join(db_dir_path, 'projects')
ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(root, 'database')



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

#
# Project operations
#

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
            remove_database_json_val('projects', name)
            return True,
        except:
            return False, 'Failed to delete the project'
    else:
        return False, 'Project doesn\'t exist'


def modify_project_desc(name: str, desc: str) -> (bool, str):
    pass


def get_project_info(name: str) -> dict:
    if project_exist(name):
        proj_json = json.load(
            open(os.path.join(proj_dir_path, name, 'properties.json'),
                 'r', encoding='utf-8'))
        return proj_json
    else:
        return {}


def get_project_list(info: bool = True) -> list:
    db_json = json.load(open(db_json_path, 'r', encoding='utf-8'))
    if info:
        projs = []
        for proj in db_json['projects']:
            info = get_project_info(proj)
            if info:
                projs.append(info)
        return projs
    else:
        return db_json['projects']


#
# Task operations
#

def create_task(task_name: str, proj_name: str,
                desc: str = '', conf: str = '',
                tag: str = '') -> (bool, str):
    pass


def delete_task(task_name: str, proj_name: str) -> (bool, str):
    pass


def modify_task_desc(task_name: str, proj_name: str, desc: str) -> (bool, str):
    pass


def set_task_status(task_name: str, proj_name: str, status: str) -> (bool, str):
    pass


def modify_task_tags(task_name: str, proj_name: str, tags: str) -> (bool, str):
    pass


def modify_task_conf(task_name: str, proj_name: str, conf: str) -> (bool, str):
    pass


#
# Result operations
#
RESULT_APPEND_FUNC = {}


def add_result(proj_name: str, task_name: str, rst_name: str, rst_type: str
               ) -> (bool, str):
    pass


def remove_result(proj_name: str, task_name: str, rst_name: str) -> (bool, str):
    pass


def rst_append_func(func):
    """Decorator function to register result appending functions.
    :param func: Result appending function.
    """
    def register_func(name):
        RESULT_APPEND_FUNC[name] = func
    return register_func


def append_result_val(proj_name: str, task_name: str, rst_name: str, rst_type: str,
                      val: list) -> (bool, str):
    """
    :param proj_name: Project name.
    :param task_name: Task name.
    :param rst_name: Result name.
    :param rst_type: Result type.
    :param val: A list of values.
    :return:
    """
    if rst_type in RESULT_APPEND_FUNC:
        return RESULT_APPEND_FUNC[rst_type](proj_name, task_name, rst_name, val)
    else:
        return False, 'Unknown result type'


@rst_append_func('table')
def append_table_val(proj_name: str, task_name: str, rst_name: str, val: list
                  ) -> (bool, str):
    """
    :param proj_name: Project name.
    :param task_name: Task name.
    :param rst_name: Result name.
    :param val: A list of values.
    :return:
    """
    pass


@rst_append_func('2dplot')
def append_2dplot_val(proj_name: str, task_name: str, rst_name: str, val: list
                   ) -> (bool, str):
    """
    :param proj_name: Project name.
    :param task_name: Task name.
    :param rst_name: Result name.
    :param val: A list of values.
    :return:
    """
    pass


class Project(object):
    def __init__(self,
                 name: str,
                 desc: str = '',
                 tasks: list = None,
                 archived: bool = False,
                 create_time: int = -1,
                 db = None
                 ):
        self.name = name
        self.desc = desc
        self.tasks = tasks if tasks else []
        self.archived = archived
        self.create_time = int(time.time()) if create_time == -1 else create_time
        self.metadata = {}
        self.db = db

    def has_task(self, name: str) -> bool:
        pass

    def create(self):
        assert self.db is not None
        proj_path = os.path.join(self.db.proj_dir_path, self.name)
        metadata_path = os.path.join(proj_path, 'metadata.json')
        # Make project directory
        os.mkdir(proj_path)
        # Create metadata.json
        metadata = {
            'name': self.name,
            'desc': self.desc,
            'tasks': self.tasks,
            'archived': self.archived,
            'create_time': self.create_time
        }
        json.dump(metadata, open(metadata_path, 'w', encoding='utf-8'))


class Database(object):
    def __init__(self, path: str = DEFAULT_DB_PATH):
        self.path = path
        self.proj_dir_path = os.path.join(path, 'projects')
        self.db_metadata_path = os.path.join(path, 'metadata.json')
        self.metadata = self.read_metadata()

    def read_metadata(self):
        return json.load(open(self.db_metadata_path, 'r', encoding='utf-8'))

    def save_metadata(self):
        json.dump(self.metadata, open(self.db_metadata_path, 'w', encoding='utf-8'))

    def add_metadata(self, key: str, val):
        """Add a key-value pair to the metadata.
        Existing value will be overwritten.
        :param key: Key to add.
        :param val: Value to add.
        """
        self.metadata[key] = val
        self.save_metadata()

    def delete_metadata(self, key: str):
        """Remove a key-value pair from the metadata.
        A KeyError will be raised if the key does not exist.
        """
        val = self.metadata.pop(key)
        self.save_metadata()
        return val

    def append_metadata_item(self, key: str, item: str):
        """Append a value to a list type metadata value.
        :param key: Metadata key.
        :param item: Item to append.
        """
        if key in self.metadata:
            if type(self.metadata[key]) is list:
                self.metadata[key].append(item)
                self.save_metadata()
            else:
                raise TypeError('{} is not a list type value'.format(key))
        else:
            self.metadata[key] = [item]
            self.save_metadata()

    def remove_metadata_item(self, key: str, item: str):
        """Remove a value from a list type metadata value.
        :param key: Metadata key.
        :param item: Item to remove.
        """
        if key in self.metadata:
            if type(self.metadata[key]) is list:
                self.metadata[key].remove(item)
                self.save_metadata()
            else:
                raise TypeError('{} is not a list type value'.format(key))
        else:
            raise KeyError('{} does not exist')

    def has_project(self, name: str) -> bool:
        """Check if a project exists by name.
        :param name: Project name.
        """
        proj_path = os.path.join(self.proj_dir_path, name)
        return os.path.exists(proj_path) and os.path.isdir(proj_path)

    def create_project(self, name: str, desc: str = '') -> Project:
        """Create a project.
        :param name: Project name.
        :param desc: Project description.
        """
        if self.has_project(name):
            raise ValueError('project {} exists'.format(name))

        proj = Project(name, desc)
        proj.create()
        self.add_metadata('projects', name)

        return proj

    def delete_project(self, name: str):
        if self.has_project(name):
           shutil.rmtree(os.path.join(self.proj_dir_path, name))
           self.remove_metadata_item('projects', name)
        else:
            raise ValueError('project {} does not exists'.format(name))





