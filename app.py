from flask import Flask 
from flask import request, send_file
import spacy
import pickle
import json
from spacy_lookup import Entity

app = Flask(__name__)

@app.route('/extractTags')
def extractTags():
	query = request.args.get('query')
	with open('tags.txt','r') as fp:
		tags = pickle.load(fp)
		nlp = spacy.load('en')
		entity = Entity(keywords_list=tags)
		nlp.add_pipe(entity,last=True)
		# txt = unicode(query,encoding="utf-8")
		doc =  nlp(query)
		response = {"data":doc._.entities}
		return json.dumps(response)