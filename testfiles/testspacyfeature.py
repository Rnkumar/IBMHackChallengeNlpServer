import spacy
import string

nlp = spacy.load('en')

punctuations = string.punctuation
result = []
doc = nlp(input("Enter the text: "))
print("text\tidx\tlemma\tis_punct\tis_space\tshape\tpos\ttag\t\n")
for token in doc:
    print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(
            token.text,
            token.idx,
            token.lemma_,
            token.is_punct,
            token.is_space,
            token.shape_,
            token.pos_,
            token.tag_
        ))
    if token.is_punct:
        result.append(token.text)
    elif str(token.pos_) == "PUNCT":
        result.append(token.text)
    else:
        for i in punctuations:
            if i in token.text:
                result.append(token.text)
                break
print(result)