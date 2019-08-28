from flask import Flask 
from flask import request, send_file
import spacy
import pickle
import json
from spacy_lookup import Entity
from spacy_hunspell import spaCyHunSpell
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/extractTags')
def extractTags():
	query = request.args.get('query')
	with open('tags.txt','rb') as fp:
		tags = pickle.load(fp)
		nlp = spacy.load('en')
		tags.remove('connect')
		entity = Entity(keywords_list=tags)
		nlp.add_pipe(entity,last=True)
		# txt = unicode(query,encoding="utf-8")
		doc =  nlp(query)
		tagstaken = []
		for name,index,named in doc._.entities:
			tagstaken.append(name)
		response = {"data":tagstaken}
		return json.dumps(response)

@app.route('spellcheck')
def spellCheck():
	query = request.args.get('query')
	nlp = spacy.load('en_core_web_lg')
	hunspell = spaCyHunSpell(nlp,'linux')
	nlp.add_pipe(hunspell)
	doc = nlp(query)
	original_data = [token.text for token in doc]
	for i,data in enumerate(doc):
		if(not data._.hunspell_spell):
			suggestions = data._.hunspell_suggest
			suggestions_vocab = convertToWordVectors(suggestions)
			result = [ data.similarity(ind) for ind in suggestions_vocab]
			max_word_index = result.index(max(result))
			word = suggestions[max_word_index]
			original_data[i]=word
	response = " ".join(original_data)
	return json.dumps({"data":response})