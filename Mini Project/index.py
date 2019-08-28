import sys
import operator
from collections import defaultdict
import timeit
import re
import os
import pdb
import xml.sax
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *
import Stemmer
import threading
from unidecode import unidecode
from tqdm import tqdm


currPage = 0

stemmer = Stemmer.Stemmer('english')
stop_words =  stopwords.words('english')


def Indexing(title, body, info, categories, links, references):

    global currPage
    # global fileCount
    global indexMap
    # global offset
    global dictID

    ID = currPage
    words = defaultdict(int)
    d = defaultdict(int)
    for word in self.title:
        d[word] += 1
        words[word] += 1
    title = d
        
    d = defaultdict(int)
    for word in self.body:
        d[word] += 1
        words[word] += 1
    body = d

    d = defaultdict(int)
    for word in self.info:
        d[word] += 1
        words[word] += 1
    info = d
    
    d = defaultdict(int)
    for word in self.categories:
        d[word] += 1
        words[word] += 1
    categories = d
        
    d = defaultdict(int)
    for word in self.links:
        d[word] += 1
        words[word] += 1
    links = d
        
    d = defaultdict(int)
    for word in self.references:
        d[word] += 1
        words[word] += 1
    references = d
    
    for word in words.keys():
        t = title[word]
        b = body[word]
        i = info[word]
        c = categories[word]
        l = links[word]
        r = references[word]
        string = 'd'+str(ID)
        if t:
            string += 't' + str(t)
        if b:
            string += 'b' + str(b)
        if i:
            string += 'i' + str(i)
        if c:
            string += 'c' + str(c)
        if l:
            string += 'l' + str(l)
        if r:
            string += 'r' + str(r)
        
        indexMap[word].append(string)
        
        currPage += 1


def stemming(text):
    # Should not be used. use dict instead.    
    return stemmer.stemWords(text)

def tokenization(data):

    data = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', data)
    data = re.sub(r'http[^\ ]*\ ', r' ', data)
    data = re.sub(r'\—|\%|\$|\'|\||\.|\*|\[|\]|\:|\;|\,|\{|\}|\(|\)|\=|\+|\-|\_|\#|\!|\`|\"|\?|\/|\>|\<|\&|\\|\n', r' ', data)
    return data.split()


def removeStopwords(text):
    
    # need to check for faster performance. O(n^2) the following loop.
    return [x for x in text if x not in stop_words]

def processTitle(title):
    
    title = tokenization(title)
    title = removeStopwords(title)
    title = stemming(title)
    return title


def processBody(text):
    data = re.sub(r'\{\{.*\}\}', r' ', text)
    data = tokenization(data)
    data = removeStopwords(data)
    data = stemming(data)
    return data

def processInfo(text):
    data = text.split('\n')
    flag = 0
    info = []
    for line in data:
        if re.match(r'\{\{infobox', line):
            flag = 1
            info.append(re.sub(r'\{\{infobox(.*)', r'\1', line))
        elif flag == 1:
            if line == '}}':
                flag = 0
                continue
            info.append(line)

    data = tokenization(' '.join(info))
    data = removeStopwords(data)
    data = stemming(data)
    return data

def processRef(text):

    data = text.split('\n')
    refs = []
    for line in data:
        if re.search(r'<ref', line):
            refs.append(re.sub(r'.*title[\ ]*=[\ ]*([^\|]*).*', r'\1', line))
    data = tokenization(' '.join(refs))
    data = removeStopwords(data)
    data = stemming(data)
    return data


def processCat(text):
    
    data = text.split('\n')
    categories = []
    for line in data:
        if re.match(r'\[\[category', line):
            categories.append(re.sub(r'\[\[category:(.*)\]\]', r'\1', line))
    
    data = tokenization(' '.join(categories))
    data = removeStopwords(data)
    data = stemming(data)
    return data


def processLinks(text):
    
    data = text.split('\n')
    links = []
    for line in data:
        if re.match(r'\*[\ ]*\[', line):
            links.append(line)
    
    data = tokenization(' '.join(links))
    data = removeStopwords(data)
    data = stemming(data)
    return data


def preprocess(title, text):
    

    text = text.encode("ascii", errors="ignore").decode()
    text = text.lower()
    text = text.replace("== references ==", "==references==")
    text = text.split("==references==")
    title = title.encode("ascii", errors="ignore").decode()
    title = title.lower()
    title = processTitle(title)
    
    body = processBody(text[0])
    info = processInfo(text[0])

    if len(text) != 1:
        ref =  processRef(text[1])
        links = processLinks(text[1])
        cat = processCat(text[1])

    else:
        ref = []
        links = []
        cat = []
    
    return title, info, body, ref, links, cat


class docHandler(xml.sax.ContentHandler):

    def __init__(self):
        self.tag = ""
        self.title = ""
        self.text = ""

    def characters(self, content):
        # check the ids
        if self.tag == "title":
            self.title += content
        elif self.tag == "text":
            self.text += content

    def startElement(self, tag, attr):
        self.tag = tag

    def endElement(self, tag):

        if tag == "page":
            title, info, body, ref, links, cat = preprocess(self.title, self.text)
            self.tag = ""
            self.title = ""
            self.text = ""
            # print("title: ", title)
            # print("body: ", body)
            # print("info: ", info)
            # print("categories: ", cat)
            # print("links: ", links)
            # print("references: ", ref)


def Parser(filename):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    textExtractor = docHandler()
    parser.setContentHandler(textExtractor)
    parser.parse(filename)


if __name__ == "__main__":
    Parser(sys.argv[1])
