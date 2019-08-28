from flask import Flask 
from flask import request, send_file
import spacy
import pickle
import json
import string	
from spacy_lookup import Entity
from spacy_hunspell import spaCyHunSpell
from flask_cors import CORS
larger_nlp = spacy.load('en_core_web_lg')
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

@app.route('/spellcheck')
def spellCheck():
	query = request.args.get('query')
	hunspell = spaCyHunSpell(larger_nlp,'linux')
	larger_nlp.add_pipe(hunspell)
	doc = larger_nlp(query)
	original_data = [token.text for token in doc]
	for i,data in enumerate(doc):
		if(not data._.hunspell_spell):
			suggestions = data._.hunspell_suggest
			suggestions_vocab = [larger_nlp.vocab[suggestion] for suggestion in suggestions]
			result = [ data.similarity(ind) for ind in suggestions_vocab]
			max_word_index = result.index(max(result))
			word = suggestions[max_word_index]
			original_data[i]=word
	response = " ".join(original_data)
	return json.dumps({"data":response})


@app.route('/extensionextractor')
def extensionExtractor():
	query = request.args.get('query')
	nlp = spacy.load('en')
	punctuations = string.punctuation

	response = []
	doc = nlp(query)
	for token in doc:
		if token.is_punct:
			response.append(token.text)
		elif str(token.pos_) == "PUNCT":
			response.append(token.text)
		else:
			for i in punctuations:
				if i in token.text:
					response.append(token.text)
					break
	return json.dumps({"data":response})