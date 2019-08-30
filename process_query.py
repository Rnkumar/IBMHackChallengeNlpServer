import spacy
import pickle

import string
from spacy_lookup import Entity
from spacy.tokens import Token
from spacy_hunspell import spaCyHunSpell
import requests
import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

nlp = spacy.load('en_core_web_lg')


class AnswerData:

    def __init__(self, answer):
        self.answer = answer
        self.comments = answer.comments
        self.score = None
        self.label = None

    def set_score_and_label(self, data):
        self.label = data.label
        self.score = data.score

    def __gt__(self, answer_obj):
        return self.score > answer_obj.score


def extract_tags(query):
    with open('tags.txt', 'rb') as fp:
        tags = pickle.load(fp)
        entity = Entity(keywords_list=tags)
        nlp.add_pipe(entity, name="entity", last=True)
        doc = nlp(query)
        tags_taken, tag_indices = [], []
        for name, index, named in doc._.entities:
            tag_indices.append(index)
            tags_taken.append(name)
        nlp.remove_pipe("entity")
        return tags_taken, tag_indices


def spell_check(query, indices_to_ignore):
    hunspell = spaCyHunSpell(nlp, 'linux')
    nlp.add_pipe(hunspell, name="hunspell")
    doc = nlp(query)
    original_data = [token.text for token in doc]
    for i, data in enumerate(doc):
        if i in indices_to_ignore:
            continue
        if not data._.hunspell_spell:
            suggestions = data._.hunspell_suggest
            suggestions_vocab = [nlp.vocab[suggestion] for suggestion in suggestions]
            result = [data.similarity(ind) for ind in suggestions_vocab]
            max_word_index = result.index(max(result))
            word = suggestions[max_word_index]
            original_data[i] = word
    response = " ".join(original_data)
    nlp.remove_pipe('hunspell')
    Token.remove_extension("hunspell_spell")
    Token.remove_extension("hunspell_suggest")
    return response


def extension_extractor(query):
    punctuations = string.punctuation
    response = []
    doc = nlp(query)
    for index, token in enumerate(doc):
        if token.is_punct:
            response.append(index)
        elif str(token.pos_) == "PUNCT":
            response.append(index)
        else:
            for i in punctuations:
                if i in token.text:
                    response.append(index)
                    break
    return response


def send_request(question,tag):
    url = "https://api.stackexchange.com//2.2/search/advanced?order=desc&sort=relevance&q=" + question + "&tagged=" + tag + "&site=stackoverflow&filter=!0V-ZwUEu0wMbto7XPem1M8Bnq"
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        resp_json = response.json()
        if len(resp_json["items"]) == 0:
            return None,False
        return resp_json["items"],True
    else:
        return False


def validate_answers(resp_items):
    items = []
    for question in resp_items:
        if "answers" in question:
            items.append(question)
    return items


def stack_overflow_request(question, tag_set):
    #Verifying if response is present in all tags
    tag_set_str = ";".join(tag_set)
    resp_items,flag = send_request(question,tag_set_str)
    if flag:
        return validate_answers(resp_items)

    #Verfying if atleast one tag matches
    for tag in tag_set:
            resp_items, flag = send_request(question,tag)
            if not flag:
                continue
            else:
                return validate_answers(resp_items)
    return []


def sentiment_analysis(data):
    service = NaturalLanguageUnderstandingV1(
        version='2018-03-16',
        url='https://gateway-syd.watsonplatform.net/natural-language-understanding/api',
        iam_apikey='HFjq-HFR7KeRxS09ZVWkO4mAofmcvJeU2OHxmzJ35jTN')

    response = service.analyze(
        text=data,
        features=Features(sentiment=SentimentOptions())).get_result()
    return response["sentiment"]["document"]["score"]


def process_answers(items):
    answers = []
    for question in items:
        for answer in question["answers"]:
            answers.append(answer)
    return answers


def sentiment_analysis_aggregator(answers):
    scores = []
    cnt = 0
    for answer in answers:
        data = ""
        if "comments" not in answer:
            continue
        for comment in answer["comments"]:
            data+=comment["body"]
        resp = sentiment_analysis(data)
        scores.append({"answer":answer,"score":resp})
        if cnt == 3:
            break
        cnt+=1
    print([a["score"] for a in scores])
    scores = sorted(scores, key = lambda i: i['score'],reverse=True) 
    return [a["answer"] for a in scores]

def process_query(user_query,sentiment):
    indices = extension_extractor(user_query)
    tag_list, tagIndices = extract_tags(user_query)

    spell_correct = spell_check(user_query, indices + tagIndices)

    so_question_items = stack_overflow_request(spell_correct, tag_list)
    answers = process_answers(so_question_items)
    if sentiment:
        answers = sentiment_analysis_aggregator(answers)
    return so_question_items,answers

if __name__ == "__main__":
    so_question_items = stack_overflow_request("how to run node app.js",[])
    answers = process_answers(so_question_items)
    answers = sentiment_analysis_aggregator(answers)
    # print(len(answers))
    # print(answers[0].keys())
    #sentiment_analysis_aggregator(answers)
    # print(sentiment_analysis("I fell really bad towards how i get treated!"))

    # print(len(so_question_items))
    # print(process_answers_apply_sentiment(so_question_items))
    # print(spell_correct)
    # print(tag_list)
