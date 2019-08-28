import spacy
from spacy_hunspell import spaCyHunSpell


def convertToWordVectors(suggestions):
    return [nlp.vocab[suggestion] for suggestion in suggestions]

nlp = spacy.load('en_core_web_lg')
hunspell = spaCyHunSpell(nlp,'linux')
nlp.add_pipe(hunspell)

doc = nlp('hwo to read data')
print(doc)
original_data = [token.text for token in doc]
for i,data in enumerate(doc):
    if(not data._.hunspell_spell):
        suggestions = data._.hunspell_suggest
        suggestions_vocab = convertToWordVectors(suggestions)
        result = [ data.similarity(ind) for ind in suggestions_vocab]
        max_word_index = result.index(max(result))
        word = suggestions[max_word_index]
        original_data[i]=word
print(" ".join(original_data))