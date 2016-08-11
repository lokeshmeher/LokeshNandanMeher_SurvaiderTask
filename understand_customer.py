from flask import Flask, render_template
from flask_pymongo import PyMongo
import json
from bson import json_util

app = Flask(__name__)

# Database setup
app.config['MONGO_DBNAME'] = 'appdb_free_2'
app.config['MONGO_URI'] = 'mongodb://lokesh:pa$$w0rd123@ds023634.mlab.com:23634/appdb_free_2'
mongo = PyMongo(app)


# Run only once.
@app.cli.command('initdb')
def command_initdb():
	"""Imports data from json file into database."""
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
	"""Shows overall sentiments for all units."""
	reviews = mongo.db.reviews
	cursor = reviews.aggregate(
		[
			{'$group': {'_id': '$sentiment', 'count': {'$sum': 1}}}
		]
	)
	sentiments = [doc for doc in cursor]
	context = {}
	total_reviews = sum([sentiment['count'] for sentiment in sentiments])
	for sentiment in sentiments:
		# for e.g., {'positive': 62.05}. The value denotes percentage.
		context[sentiment['_id'].lower()] = sentiment['count']/total_reviews * 100

	relation = mongo.db.relation
	cursor = relation.find()	# Since only one hotel chain is present
	context['units'] = cursor[0]['units']

	return render_template('home.html', **context)


@app.route('/unit/<id>')
def unit_details(id):
	"""Shows sentiments and reviews for individual hotel unit."""
	relation = mongo.db.relation
	context = {}
	for unit in relation.find()[0]['units']:
		if unit['property_id'] == id:
			context['unit_name'] = unit['name']
			break
	context['unit_id'] = id

	reviews = mongo.db.reviews
	cursor = reviews.aggregate(
		[
			{'$match': {'property_id': id}},
			{'$group': {'_id': '$sentiment', 'count': {'$sum': 1}}},
		]
	)
	sentiments = [doc for doc in cursor]
	total_reviews = sum([sentiment['count'] for sentiment in sentiments])
	for sentiment in sentiments:
		context[sentiment['_id'].lower()] = sentiment['count']/total_reviews * 100

	unit_reviews = reviews.find({'property_id': id})
	context['unit_reviews'] = unit_reviews

	return render_template('unit_details.html', **context)


@app.route('/api/get_reviews/<hotel_id>/<int:start_index>/<int:num_elems>')
def get_reviews(hotel_id, start_index, num_elems):
	reviews = mongo.db.reviews
	try:
		cursor = reviews.find(
			{'property_id': hotel_id}
		)[start_index:(start_index + num_elems)]
	except IndexError:
		data_exhausted = True
		revs = []
	else:
		data_exhausted = False
		revs = [doc for doc in cursor]
	return json_util.dumps(
		{
			'dataExhausted': data_exhausted,
			'reviews': revs
		}
	)
