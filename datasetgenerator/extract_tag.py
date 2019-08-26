import pickle
import pandas as pd


tag1_dataset = pd.read_csv('tag1.csv')
tag2_dataset = pd.read_csv('tag2.csv')

result = []

for i in range(len(tag1_dataset)):
    data = str(tag1_dataset.iloc[i]['TagName'])
    if data not in ["using","analysis","connect"]:
        result.append(str(tag1_dataset.iloc[i]['TagName']))

for i in range(len(tag2_dataset)):
    data = str(tag2_dataset.iloc[i]['TagName'])
    if data not in ["using","analysis","connect"]:
        result.append(str(tag2_dataset.iloc[i]['TagName']))


with open("tags.txt", "wb") as fp:
    pickle.dump(result, fp)