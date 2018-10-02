import os
import re
import json
import time
import shutil
import logging
import traceback

logger = logging.getLogger()

root = os.path.dirname(os.path.abspath(__file__))
# db_dir_path = os.path.join(root, 'database')
# db_json_path = os.path.join(db_dir_path, 'database.json')
# proj_dir_path = os.path.join(db_dir_path, 'projects')
# ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(root, 'database')

boolean = lambda x : x if type(x) is bool else x.lower() == 'true'

def validate_name(name: str) -> bool:
    return re.match('^[0-9a-zA-Z _-]{2,50}$', name) is not None


class Container(object):
    def __init__(self):
        self.metadata = {}
        self.metadata_path = None

    def read_metadata(self):
        return json.load(open(self.metadata_path, 'r', encoding='utf-8'))

    def save_metadata(self):
        json.dump(self.metadata, open(self.metadata_path, 'w', encoding='utf-8'))

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


class Dict(object):

    def __init__(self, path):
        self.path = path
        self.allowed_types = {}
        self.formatters = {}
        self.dictionary = {}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            self.dictionary = json.load(open(self.path, 'r', encoding='utf-8'))

    def save(self):
        json.dump(self.dictionary, open(self.path, 'w', encoding='utf-8'))

    def insert(self, key, value, val_type='str', overwrite: bool = False):
        if val_type not in self.allowed_types:
            raise ValueError('Unknown value type: {}'.format(val_type))
        value = self.formatters[val_type](value)
        if key not in self.dictionary or overwrite:
            self.dictionary[key] = {'value': value, 'type': val_type}
        self.save()

    def delete(self, key):
        return self.dictionary.pop(key)

    def get(self, key):
        return self.dictionary.get(key)

    def append(self, key, value, val_type):
        raise NotImplementedError()


class Result(Dict):
    def __init__(self, path):
        super().__init__(path)
        self.allowed_types = {'str', 'int', 'float', 'list', 'file',
                              'table', 'plot2d', 'html', 'json'}
        self.formatters = {
            'str': lambda x: x,
            'file': lambda x: x,
            'int': lambda x: int(x),
            'float': lambda x: float(x),
            'list': lambda x: json.loads(x),
            'json': lambda x: json.loads(x),
            'html': lambda x: x,
            'table': lambda x: {'cols': json.loads(x), 'data': []},
            'plot2d': lambda x: {'series': json.loads(x), 'data': []}
        }

    def table_formatter(self, value: str):
        return json.dumps({'cols': json.loads(value), 'rows': []})

    def plot2d_formatter(self, value: str):
        pass

    def append(self, key, value, val_type):
        if val_type in {'table', 'plot2d'}:
            self.dictionary[key]['value']['data'].append(json.loads(value))
        else:
            raise ValueError('Unknown value type: {}'.format(val_type))
        self.save()


class Config(Dict):
    def __init__(self, path):
        super().__init__(path)
        self.allowed_types = {'str', 'int', 'float', 'file', 'list', 'json'}
        self.formatters = {
            'str': lambda x: x,
            'file': lambda x: x,
            'int': lambda x: int(x),
            'float': lambda x: float(x),
            'list': lambda x: json.loads(x),
            'json': lambda x: json.loads(x),
        }

    def append(self, key, value, val_type):
        pass


class Task(Container):

    def __init__(self,
                 name: str,
                 metadata: dict = None,
                 path: str = ''
                 ):
        super().__init__()
        self.name = name
        self.path = path
        self.metadata_path = os.path.join(path,
                                          'metadata.json') if path else None
        self.config_path = os.path.join(path, 'config.json') if path else None
        self.result_path = os.path.join(path, 'result.json') if path else None
        if metadata is None:
            if os.path.exists(self.metadata_path):
                self.metadata = self.read_metadata()
            else:
                self.metadata = {}
        else:
            self.metadata = metadata

    def has_subtask(self, name: str) -> bool:
        return name in self.metadata.get('subtasks', [])

    def create(self):
        os.mkdir(self.path)
        os.mkdir(os.path.join(self.path, 'subtasks'))
        self.save_metadata()

    def create_subtask(self, name: str):
        if self.has_subtask(name):
            raise ValueError('Subtask {} already exists'.format(name))
        if not validate_name(name):
            raise ValueError('Invalid task name')

        task = Task(name, path=os.path.join(self.path, 'subtasks', name))
        task.create()
        task.add_metadata('name', name)
        task.add_metadata('identifier', '{}/{}'.format(
            self.metadata['identifier'], name))
        task.add_metadata('create_time', int(time.time()))
        task.add_metadata('status', 'running')
        task.add_metadata('subtasks', [])
        task.add_metadata('desc', '')
        self.append_metadata_item('subtasks', name)

    def delete_subtask(self, name: str):
        if self.has_subtask(name):
            shutil.rmtree(os.path.join(self.path, 'subtasks', name))
            self.remove_metadata_item('subtasks', name)
        else:
            raise ValueError('Subtask {} does not exists'.format(name))

    def get_subtask(self, name: str):
        if self.has_subtask(name):
            return Task(name, path=os.path.join(self.path, 'subtasks', name))
        else:
            raise ValueError('Subtask {} does not exists'.format(name))

    def insert_result(self, key: str, value: str, val_type: str,
                      overwrite: bool = False):
        result = Result(self.result_path)
        result.insert(key, value, val_type, overwrite)

    def delete_result(self, key: str):
        result = Result(self.result_path)
        result.delete(key)

    def append_result(self, key: str, value: str, val_type: str):
        result = Result(self.result_path)
        result.append(key, value, val_type)

    def get_result_value(self, key: str):
        result = Result(self.result_path)
        return result.get(key)

    def get_result(self):
        return Result(self.result_path).dictionary

    def insert_config(self, key: str, value: str, val_type: str,
                      overwrite: bool = False):
        config = Config(self.config_path)
        config.insert(key, value, val_type, overwrite)

    def delete_config(self, key: str):
        config = Config(self.config_path)
        config.delete(key)

    def get_config(self):
        return Config(self.config_path).dictionary

    def get_config_value(self, key: str):
        config = Config(self.config_path)
        return config.get(key)

    def create_child(self, name: str):
        return self.create_subtask(name)

    def delete_child(self, name: str):
        return self.delete_child(name)

    def has_child(self, name: str):
        return self.has_subtask(name)

    def get_child(self, name: str):
        return self.get_subtask(name)

    def list_children(self, info: bool = False):
        tasks = self.metadata.get('subtasks', [])
        if info:
            tasks = [self.get_child(task).metadata for task in tasks]
        return tasks


class Project(Container):
    def __init__(self,
                 name: str,
                 metadata: dict = None,
                 path: str = '',
                 ):
        super().__init__()

        self.name = name
        self.path = path
        self.metadata_path = os.path.join(path, 'metadata.json') if path else None
        if metadata is None:
            if os.path.exists(self.metadata_path):
                self.metadata = self.read_metadata()
            else:
                self.metadata = {}
        else:
            self.metadata = metadata

    def has_task(self, name: str) -> bool:
        return name in self.metadata.get('tasks', [])

    def create(self):
        os.mkdir(self.path)
        os.mkdir(os.path.join(self.path, 'tasks'))
        self.save_metadata()

    def create_task(self, name: str):
        if self.has_task(name):
            raise ValueError('Task {} already exists'.format(name))
        if not validate_name(name):
            raise ValueError('Invalid task name')

        task = Task(name, path=os.path.join(self.path, 'tasks', name))
        task.create()
        task.add_metadata('name', name)
        task.add_metadata('create_time', int(time.time()))
        task.add_metadata('identifier', '{}/{}'.format(
            self.metadata['identifier'], name))
        task.add_metadata('status', 'running')
        task.add_metadata('desc', '')
        task.add_metadata('subtasks', [])
        self.append_metadata_item('tasks', name)

    def delete_task(self, name: str):
        if self.has_task(name):
            shutil.rmtree(os.path.join(self.path, 'tasks', name))
            self.remove_metadata_item('tasks', name)
        else:
            raise ValueError('Task {} does not exists'.format(name))

    def get_task(self, name: str):
        if self.has_task(name):
            return Task(name, path=os.path.join(self.path, 'tasks', name))
        else:
            raise ValueError('Task {} does not exists'.format(name))

    def has_child(self, name: str):
        return self.has_task(name)

    def create_child(self, name: str):
        return self.create_task(name)

    def delete_child(self, name: str):
        return self.delete_child(name)

    def get_child(self, name: str):
        return self.get_task(name)

    def list_children(self, info: bool = False):
        tasks = self.metadata.get('tasks', [])
        if info:
            tasks = [self.get_child(task).metadata for task in tasks]
        return tasks


class Database(Container):
    # TODO: rewrite api
    # TODO: combine similar api funcs (e.g., insert_task_config, insert_task_result)
    def __init__(self, path: str = DEFAULT_DB_PATH):
        super().__init__()

        self.path = path
        self.proj_dir_path = os.path.join(path, 'projects')
        self.metadata_path = os.path.join(path, 'metadata.json')
        if os.path.exists(self.metadata_path):
            self.metadata = self.read_metadata()
        else:
            self.initialize_database()

        self.ops = {
            'create_project': (self.create_project, [('name', str, None)]),
            'delete_project': (self.delete_project, [('name', str, None)]),
            'list_projects': (self.list_projects, [('info', boolean, False)]),
            'list_children': (self.list_children,
                              [('parent', str, None), ('info', boolean, False)]),
            'create_task': (self.create_task,
                            [('parent', str, None), ('name', str, None)]),
            'insert_task_result': (self.insert_task_result,
                                   [('identifier', str, None), ('key', str, None),
                                    ('value', str, None), ('val_type', str, None),
                                    ('overwrite', boolean, False)]),
            'delete_task_result': (self.delete_task_result,
                                   [('identifier', str, None), ('key', str, None)]),
            'insert_task_config': (self.insert_task_config,
                                   [('identifier', str, None), ('key', str, None),
                                    ('value', str, None), ('val_type', str, None),
                                    ('overwrite', boolean, False)]),
            'delete_task_config': (self.delete_task_config,
                                   [('identifier', str, None), ('key', str, None)]),
            'append_task_result': (self.append_task_result,
                                   [('identifier', str, None), ('key', str, None),
                                    ('value', str, None),
                                    ('val_type', str, None)]),
            'update_child_metadata': (self.update_child_metadata,
                                      [('identifier', str, None),
                                       ('metadata', str, None)]),
            'get_task_configs': (self.get_task_configs, [('identifier', str, None)]),
            'get_task_results': (self.get_task_results, [('identifier', str, None)]),
        }

    def initialize_database(self):
        logger.info('Initializing database...')
        self.metadata = {
            'projects': [],
            'archived': [],
            'create_time': int(time.time())
        }
        self.save_metadata()
        os.mkdir(self.proj_dir_path)

    def has_project(self, name: str) -> bool:
        """Check if a project exists by name.
        :param name: Project name.
        """
        return name in self.metadata.get('projects', [])

    def create_project(self, name: str):
        """Create a project.
        :param name: Project name.
        :param desc: Project description.
        """
        if self.has_project(name):
            raise ValueError('Project {} exists'.format(name))
        if not validate_name(name):
            raise ValueError('Invalid project name')

        proj = Project(name,
                       path=os.path.join(self.proj_dir_path, name))
        proj.create()
        proj.add_metadata('name', name)
        proj.add_metadata('identifier', name)
        proj.add_metadata('create_time', int(time.time()))
        proj.add_metadata('tasks', [])
        proj.add_metadata('desc', '')
        self.append_metadata_item('projects', name)

    def delete_project(self, name: str):
        if self.has_project(name):
           shutil.rmtree(os.path.join(self.proj_dir_path, name))
           self.remove_metadata_item('projects', name)
        else:
            raise ValueError('Project {} does not exist'.format(name))

    def get_project(self, name: str):
        if self.has_project(name):
            return Project(name, path=os.path.join(self.proj_dir_path, name))
        else:
            raise ValueError('Project {} does not exist'.format(name))

    def list_projects(self, info: bool = False):
        projs = self.metadata.get('projects', [])
        if info:
            projs = [self.get_project(proj).metadata for proj in projs]
            projs_ = []
            for proj in projs:
                if 'tasks' in proj:
                    proj['tasks'] = self.list_children(proj['identifier'], info=True)
                else:
                    proj['tasks'] = []
                projs_.append(proj)
            projs = projs_
        return projs

    def list_children(self, parent, info: bool = False):
        parent = self.get_child(parent)
        return parent.list_children(info=info)

    def get_child(self, name: str):
        if '/' not in name:
            if self.has_project(name):
                return self.get_project(name)
            else:
                raise ValueError('Project {} does not exist'.format(name))
        else:
            name = name.split('/')
            current = self.get_project(name[0])
            tasks = name[1:]
            for task in tasks:
                current = current.get_child(task)
            return current

    def create_task(self, parent: str, name: str):
        parent = self.get_child(parent)
        parent.create_child(name)

    def insert_task_result(self, identifier: str, key: str, value: str,
                           val_type: str, overwrite: bool = False):
        node = self.get_child(identifier)
        node.insert_result(key, value, val_type, overwrite)

    def delete_task_result(self, identifier: str, key: str):
        node = self.get_child(identifier)
        node.delete_result(key)

    def append_task_result(self, identifier: str, key: str, value: str,
                           val_type: str):
        node = self.get_child(identifier)
        node.append_result(key, value, val_type)

    def get_task_results(self, identifier: str):
        node = self.get_child(identifier)
        return node.get_result()

    def insert_task_config(self, identifier: str, key: str, value: str,
                           val_type: str, overwrite: bool = False):
        node = self.get_child(identifier)
        node.insert_config(key, value, val_type, overwrite)

    def delete_task_config(self, identifier: str, key: str):
        node = self.get_child(identifier)
        node.delete_config(key)

    def get_task_configs(self, identifier: str):
        node = self.get_child(identifier)
        return node.get_config()

    def update_child_metadata(self, identifier: str, metadata: str):
        node = self.get_child(identifier)
        for k, v in json.loads(metadata).items():
            node.add_metadata(k, v)

    def update_metadata(self, metadata):
        for k, v in json.loads(metadata).items():
            self.add_metadata(k, v)

    def api(self, op, args):
        try:
            if op in self.ops:
                op_func, op_args = self.ops[op]
                args_ = {}
                for arg, arg_type, arg_default in op_args:
                    val = args.get(arg, arg_default)
                    if val is not None and arg_type is not None:
                        val = arg_type(val)
                    args_[arg] = val
                rst = op_func(**args_)
                return True, rst
            else:
                return False, 'Unknown operation: {}'.format(op)
        except Exception as e:
            traceback.print_exc()
            return False, str(e)
