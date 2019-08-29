from flask import Flask
from flask import request
import json
import  process_query as pq
from flask_cors import CORS

# larger_nlp = spacy.load('en_core_web_lg')
app = Flask(__name__)
CORS(app)


@app.route('/fetchdata')
def fetchdata():
    query = request.args.get('query')
    response = pq.process_query(query)
    return json.dumps({"items": response})
