from flask import Flask
from flask import render_template
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps

app = Flask(__name__)

MONGODB_HOST = 'ec2-54-191-245-35.us-west-2.compute.amazonaws.com'
MONGODB_PORT = 27017
DBS_NAME = 'miner_io'
COLLECTION_NAME = 'GLD'
FIELDS = {'_id': False, 'block_reward': True, 'daily_profit': True, 'difficulty': True, 'exchange_rate': True, 'hash_rate': True, 'timestamp': True, 'uncertainty': True}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/coinhopper.io/app")
def donorschoose_projects():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=FIELDS)
    json_projects = []
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    connection.close()
    return json_projects

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)

# Visit: http://localhost:5000/coinhopper.io/app to see DB queries