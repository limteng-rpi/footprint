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


def validate_name(name: str) -> bool:
    return re.match('^[0-9a-zA-Z_-]{2,50}$', name) is not None


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


class Config(object):

    def __init__(self):
        pass


class Result(object):

    def __init__(self, name: str):
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
            raise ValueError('Subtask {} already exists')
        if not validate_name(name):
            raise ValueError('Invalid task name')

        task = Task(name, path=os.path.join(self.path, 'subtasks', name))
        task.create()
        task.add_metadata('name', name)
        task.add_metadata('identifier', '{}/{}'.format(
            self.metadata['identifier'], name))
        self.append_metadata_item('subtasks', name)

    def delete_subtask(self, name: str):
        if self.has_subtask(name):
            shutil.rmtree(os.path.join(self.path, 'subtasks', name))
            self.remove_metadata_item('subtasks', name)
        else:
            raise ValueError('Subtask {} does not exists')

    def create_child(self, name: str):
        return self.create_subtask(name)

    def delete_child(self, name):
        return self.delete_child(name)

    def has_child(self, name):
        return self.has_subtask(name)


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
            raise ValueError('Task {} already exists')
        if not validate_name(name):
            raise ValueError('Invalid task name')

        task = Task(name, path=os.path.join(self.path, 'tasks', name))
        task.create()
        task.add_metadata('name', name)
        task.add_metadata('identifier', '{}/{}'.format(
            self.metadata['identifier'], name))
        self.append_metadata_item('tasks', name)

    def delete_task(self, name: str):
        if self.has_task(name):
            shutil.rmtree(os.path.join(self.path, 'tasks', name))
            self.remove_metadata_item('tasks', name)
        else:
            raise ValueError('Task {} does not exists')

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


class Database(Container):
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
            'create_project': (self.create_project, ['name']),
            'delete_project': (self.delete_project, ['name']),
            'create_task': (self.create_task, ['parent', 'name'])
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

    def create_project(self, name: str) -> Project:
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
        self.append_metadata_item('projects', name)

        return proj

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

    def get_child(self, name: str):
        if '/' not in name:
            if self.has_project(name):
                return self.get_project(name)
            else:
                raise ValueError('Project {} does not exist')
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

    def api(self, op, args):
        try:
            if op in self.ops:
                op_func, op_args = self.ops[op]
                args = {arg: args[arg] for arg in op_args}
                op_func(**args)
                return True, 'Success'
            else:
                return False, 'Unknown operation: {}'.format(op)
        except Exception as e:
            traceback.print_exc()
            return False, str(e)
