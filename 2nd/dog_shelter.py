from flask import Flask
from flask import request
from flask import jsonify
from flask import abort
import requests
import json
import os
import copy
import random
from faker import Faker

fake = Faker()
app = Flask(__name__)

dogs_db = [
	{'id' : '1', 'breed' : 'French bulldog', 'name' : 'Doggo', 
	'temporary guardian ID' : '12244', 'visits' : []},
	{'id' : '2', 'breed' : 'Chow Chow', 'name' : 'Sir Pup', 
	'temporary guardian ID' : '2356', 'visits' : []},
	{'id' : '3', 'breed' : 'Spaniel', 'name' : 'Coco', 
	'temporary guardian ID' : '55331', 'visits' : []},
	{'id' : '4', 'breed' : 'French bulldog', 'name' : 'Olive', 
	'temporary guardian ID' : '49612033268', 'visits' : ['1']},
	{'id' : '5', 'breed' : 'German Shepherd', 'name' : 'Rex', 
	'temporary guardian ID' : '49608052145', 'visits' : ['2']}
]


@app.route('/')
def hello():
	return'Welcome to the puppy shelter'

# GET information about all dogs from database as JSON
@app.route('/dogs', methods=['GET'])
def get_all_dogs():
	
	if(request.args.get('embedded', '') == "visit"):
		try:
			url = 'http://web2:81/visits/schedules'
			dogsCopied = copy.deepcopy(dogs_db)
			for i in range(len(dogs_db)):
				embeddedVisits = []
				for visit in dogsCopied[i]['visits']:
					r = requests.get('{}/{}'.format(url, visit))
					r = json.loads(r.text)
					embeddedVisits.append(r)
				dogsCopied[i]['visits'] = []
				dogsCopied[i]['visits'].append(embeddedVisits)
			return jsonify(dogsCopied)
		except requests.exceptions.RequestException as e:
			dogsCopied[i]['visits'] = []
			return jsonify(dogsCopied)
	else:
		return jsonify(dogs_db)

# GET any dog by any parameter
@app.route('/dogs/<parameter>', methods=['GET'])
def get_dog(parameter):
	my_dog = [ dog for dog in dogs_db if (dog['id'] == parameter or 
		dog['breed'] == parameter or dog['name'] == parameter or
		dog['temporary guardian ID'] == parameter)]
	if len(my_dog) == 0:
		abort(404)
	return jsonify(my_dog[0])



# DELETE a dog from a database by ID 
# and all its visits from visit service db (adopt)
@app.route('/dogs/<dog_id>', methods=['DELETE'])
def adopt_dog(dog_id):
	current_dog = [ dog for dog in dogs_db if (dog['id'] == dog_id )]
	if len(current_dog) == 0:
		abort(404)
	url = 'http://web2:81/visits/schedules'
	for visit_id in current_dog[0]['visits']:
		try:
			r = requests.delete('{}/{}'.format(url, visit_id))
		except requests.exceptions.RequestException as e:
			dogs_db.remove(current_dog[0])
			return str(true)
	dogs_db.remove(current_dog[0])
	return jsonify(True), 200	


# POST a dog to a database (give away)
# Name is in url, id and breed have to be provided as JSON
@app.route('/dogs', methods=['POST'])
def give_away_dog():
	current_id = int(dogs_db[len(dogs_db) - 1]['id']) + 1
	new_dog = {
	'id' : str(current_id),
	'breed' : request.json['breed'],
	'temporary guardian ID' : request.json['temporary guardian ID'],
	'name' : request.json['name']
	}
	dogs_db.append(new_dog)
	
	return jsonify(new_dog), 201
	

# PUT change a dog
# Any parameter in URL
@app.route('/dogs/<dog_id>', methods = ['PUT'])
def change_dog(dog_id):
	changed_dog = [ dog for dog in dogs_db if (dog['id'] == dog_id )]
	if len(changed_dog) == 0:
		abort(404)
	if 'name' in request.json:
		changed_dog[0]['name'] = request.json['name']
	if 'breed' in request.json:
		changed_dog[0]['breed'] = request.json['breed']
	if 'temporary guardian ID' in request.json:
		changed_dog[0]['temporary guardian ID'] = request.json['temporary guardian ID']

	return jsonify(changed_dog[0])


#### Second task 

# Get info about all visits
@app.route('/visits', methods=['GET'])
def get_all_visits():
	url = 'http://web2:81/visits/schedules'
	try:
		r = requests.get(url)
		return r.text
	except requests.exceptions.RequestException as e:  
		print(e)
		return str(e), 503

# Get visits that belong to the dog by its guardian
@app.route('/dogs/<dog_id>/visits', methods = ['GET'])
def create_visit(dog_id):
	current_dog = [ dog for dog in dogs_db if (dog['id'] == dog_id )]
	
	if len(current_dog) == 0:
		abort(404)
	
	url = 'http://web2:81/visits/schedules'
	try:
		if(request.args.get('embedded', '') == "visit"):
			copy_dog = copy.deepcopy(current_dog)
			embeddedVisits = []
			for visit in copy_dog[0]['visits']:
				r = requests.get('{}/{}'.format(url, visit))
				r = json.loads(r.text)
				embeddedVisits.append(r)
			copy_dog[0]['visits'] = []
			copy_dog[0]['visits'].append(embeddedVisits)
			return jsonify(copy_dog)
		else:
			# for visit in current_dog[0]['visits']:
			# 	if( request.args.get('embedded', '') == visit):
			# 		r = requests.get('{}/{}'.format(url, visit))
			# 		r = json.loads(r.text)
			# 		return jsonify(r)
			# 	else:
			r = requests.get('{}/{}'.format(url, current_dog[0]['temporary guardian ID']))
			if r.status_code==200:
				current_dog[0]['visits'] = []
				for visit in r.json():
					current_dog[0]['visits'].append(visit['ID'])
				return jsonify(current_dog[0])
	except requests.RequestException as e:
		current_dog[0]['visits'] = []
		return jsonify(current_dog[0])
	return jsonify(404)


# Create a new visit
@app.route('/dogs/<dog_id>/visits', methods = ['POST'])
def add_visit(dog_id):
	current_dog = [ dog for dog in dogs_db if (dog['id'] == dog_id )]
	if len(current_dog) == 0:
		abort(404)
	url = 'http://web2:81/visits/schedules'
	new_visit = {
		'AK' : current_dog[0]['temporary guardian ID'],
		'Name' : current_dog[0]['name'],
		'Surname' : current_dog[0]['breed'],
		'Date' : str(fake.date_between(start_date='today', end_date='+1y')),
		'Time' : '{}:15'.format(random.randrange(8,20))
	}
	try:
		r = requests.post(url, json=new_visit)
		current_dog[0]['visits'].append(r.json()['ID'])
		return jsonify(current_dog[0]), 201
	except requests.exceptions.RequestException as e:
		print(e)
		return str(e), 503
	

# Delete a single visit
@app.route('/dogs/<dog_id>/visits/<visit_id>', methods = ['DELETE'])
def delete_visit(dog_id, visit_id):
	current_dog = [ dog for dog in dogs_db if (dog['id'] == dog_id )]
	if len(current_dog) == 0 or len(current_dog[0]['visits']) == 0:
		abort(404)
	url = 'http://web2:81/visits/schedules'
	for index in range(len(current_dog[0]['visits'])):
		if current_dog[0]['visits'][index] == visit_id:
			try:
				r = requests.delete('{}/{}'.format(url, visit_id))
				current_dog[0]['visits'].remove(current_dog[0]['visits'][index])
				return jsonify(True), 200
			except requests.exceptions.RequestException as e:
				print(e)
				return str(e), 503	
	return jsonify(False), 404


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5000)

