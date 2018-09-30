import os
import time
import logging

from flask import Flask, request, jsonify, render_template
from argparse import ArgumentParser
from database import Database, Project, Task, Config, Result
from utils import format_time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

cur_dir = os.path.dirname(__file__)

# Parse command line arguments
parser = ArgumentParser()
parser.add_argument('--localhost', action='store_true')
parser.add_argument('--host', default=None)
parser.add_argument('--port', default=8000, type=int)
parser.add_argument('--dbpath', default=os.path.join(cur_dir, 'database'),
                    help='Path to the database')
args = parser.parse_args()

db = Database(args.dbpath)

# IP address
host = '0.0.0.0'
if args.host:
    host = args.host
elif args.localhost:
    host = '127.0.0.1'

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

# db.create_project('proj1')
# db.get_project('proj1').create_task('task1')
# db.get_project('proj1').get_task('task1').create_subtask('subtask1')

@app.route('/')
def home():
    pass

@app.route('/settings')
def setting():
    pass

@app.route('/projects')
def projects():
    return render_template('proj_view.html')

@app.route('/task/<path:identifier>')
def task(identifier):
    try:
        task = db.get_child(identifier)
        metadata = task.metadata
        metadata = {
            'name': metadata.get('name'),
            'desc': metadata.get('desc', ''),
            'create_time': format_time(metadata.get('create_time', ''))
        }
        return render_template('task_view.html', metadata=metadata)
    except Exception:
        return render_template('task_view.html')


@app.route('/api/<op>', methods=['GET', 'POST'])
def api(op):
    args = request.values
    success, msg = db.api(op, args)
    if success:
        return jsonify({'data': msg}), 200
    else:
        return jsonify({'msg': msg}), 500


if __name__ == '__main__':
    app.run(host=host, port=args.port, debug=True, threaded=True)
