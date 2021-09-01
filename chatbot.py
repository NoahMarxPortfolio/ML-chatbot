# -*- coding: utf-8 -*-
#!python3.7
import codecs
import requests
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import time

from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
intents = json.loads(codecs.open('intents.json',"r","utf-8").read(),encoding = "utf-8")
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
f = open("token.txt", "r")
bot_token = f.read()
f.close
URL = "https://api.telegram.org/bot{}/".format(str(bot_token))
    #"1075026286:AAFd8A8r5HPsbu2cJoNmms4yazhSkVlbNjY"
print(URL)
count = 0

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content
    
    
def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js
    
    
def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js
    
    
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates):
    for update in updates["result"]:
        try: 
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
        except:
            text = update["edited_message"]["text"]
            chat = update["edited_message"]["chat"]["id"]
            
        
        if text[0] != "/":
            
            send_message(text, chat)
        elif text == "/help" or text == "/Help": 
            c_reply("Beispielbefehle:", chat)
            c_reply("fisi: Inforamtionen zum beruf fachinformatiker für systemintegration", chat)
            c_reply("fian: Inforamtionen zum beruf fachinformatiker für anwendungsentwicklung", chat)
            c_reply("inka: Inforamtionen zum beruf informatik kaufmann/frau", chat)
            c_reply("/stats: gibt die der versendeten nachichten seit programmstart an", chat)
        elif text == "/stats" or text == "/Stats":
            c_reply("anzahl der versendeten nachichten seit programmstart: " + str(count), chat)
        else:
            c_reply("unbekannter befehl /help für mehr inforamtionen", chat)
            
def c_reply(text, chat_id):
    text = str(text).replace("+"," ")
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def send_message(text, chat_id):
    text = str(text).replace("+"," ")
    url = URL + "sendMessage?text={}&chat_id={}".format(chatbot_response(text), chat_id)
    get_url(url)


last_update_id = None
while True:
    updates = get_updates(last_update_id)
    if len(updates["result"]) > 0:
        last_update_id = get_last_update_id(updates) + 1
        echo_all(updates)
        count = count + 1
    time.sleep(0.5)