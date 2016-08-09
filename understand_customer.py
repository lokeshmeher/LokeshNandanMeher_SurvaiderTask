from flask import Flask
from flask_pymongo import PyMongo
import json
from pprint import pprint

app = Flask(__name__)

# Database setup
app.config['MONGO_DBNAME'] = 'appdb_free_2'
app.config['MONGO_URI'] = 'mongodb://lokesh:pa$$w0rd123@ds023634.mlab.com:23634/appdb_free_2'
mongo = PyMongo(app)

@app.cli.command('initdb')
def command_initdb():
	with open('data/relation.json') as relation_file:
		relation_data = json.load(relation_file)
		mongo.db.relation.insert(relation_data)
	with open('data/reviews.json') as reviews_file:
		reviews_data = json.load(reviews_file)
		mongo.db.reviews.insert(reviews_data)
	print('Initialized database')
