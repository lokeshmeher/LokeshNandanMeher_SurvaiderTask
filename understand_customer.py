from flask import Flask, render_template
from flask_pymongo import PyMongo
import json

app = Flask(__name__)

# Database setup
app.config['MONGO_DBNAME'] = 'appdb_free_2'
app.config['MONGO_URI'] = 'mongodb://lokesh:pa$$w0rd123@ds023634.mlab.com:23634/appdb_free_2'
mongo = PyMongo(app)

# Run only once.
@app.cli.command('initdb')
def command_initdb():
	print('Sending data to database...')
	with open('data/relation.json') as relation_file:
		relation_data = json.load(relation_file)
		relation_collection = mongo.db.relation	# create a `relation` collection
		relation_collection.insert_many(relation_data)
	with open('data/reviews.json') as reviews_file:
		reviews_data = json.load(reviews_file)
		reviews_collection = mongo.db.reviews	# create a `reviews` collection
		reviews_collection.insert_many(reviews_data)
	print('Initialized database.')

@app.route('/')
def home():
	reviews = mongo.db.reviews
	cursor = reviews.aggregate([
		{'$group': {'_id': '$sentiment', 'count': {'$sum': 1}}}
	])
	sentiments = [doc for doc in cursor]
	context = {}
	total_reviews = sum([sentiment['count'] for sentiment in sentiments])
	for sentiment in sentiments:
		# for e.g., {'positive': 62.05}. The value denotes percentage.
		context[sentiment['_id'].lower()] = sentiment['count']/total_reviews * 100
	return render_template('home.html', **context)
