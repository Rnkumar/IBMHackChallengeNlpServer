from flask import Flask 
from flask import request, send_file
import spacy
import pickle
import json
from spacy_lookup import Entity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/extractTags')
def extractTags():
	query = request.args.get('query')
	with open('tags.txt','rb') as fp:
		tags = pickle.load(fp)
		nlp = spacy.load('en')
		entity = Entity(keywords_list=tags)
		nlp.add_pipe(entity,last=True)
		# txt = unicode(query,encoding="utf-8")
		doc =  nlp(query)
		tagstaken = []
		for name,index,named in doc._.entities:
			tagstaken.append(name)
		response = {"data":tagstaken}
		return json.dumps(response)