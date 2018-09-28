import os
import logging
from flask import Flask, request, jsonify
from argparse import ArgumentParser
from database import Database, Project, Task, Config, Result

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

cur_dir = os.path.dirname(__file__)

parser = ArgumentParser()
parser.add_argument('--dbpath', default=os.path.join(cur_dir, 'database'),
                    help='Path to the database')
args = parser.parse_args()

db = Database(args.dbpath)

app = Flask(__name__)

# db.create_project('proj1')
# db.get_project('proj1').create_task('task1')
# db.get_project('proj1').get_task('task1').create_subtask('subtask1')

@app.route('/')
def home():
    pass

@app.route('/settings')
def setting():
    pass


@app.route('/api/<op>', methods=['GET', 'POST'])
def api(op):
    args = request.values
    print(args.to_dict())
    success, msg = db.api(op, args)
    return jsonify({'msg': msg}), 200 if success else 500


if __name__ == '__main__':
    app.run(debug=True)
