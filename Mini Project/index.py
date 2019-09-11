import sys
from collections import defaultdict
import re
import xml.sax
import heapq
import nltk
import json
from nltk.corpus import stopwords
import Stemmer
import timeit
from tqdm import tqdm
import threading


currPage = 0
fileCount = 0
offset = 0
fileCount = 0
inverted_index = defaultdict(list)
title_dic = defaultdict(str)

stemmer = Stemmer.Stemmer('english')
stop_words =  stopwords.words('english')



def Indexing(dic):

    global currPage
    global indexMap
    global title_dic
    global offset
    global fileCount
    
    ID = currPage
    arr = ["title", "body", "info", "cat", "links", "ref"]
    pageDic = {}
    for tag in arr:
        pageDic[tag] = defaultdict(int)

    words = defaultdict(int)

    for tag in arr:
        for word in dic[tag]:
            pageDic[tag][word] += 1
            words[word] += 1
        
    for word in words.keys():
        string = 'd' + str(currPage)

        t = pageDic["title"][word]
        if t:
            string += 't' + str(t)
        
        b = pageDic["body"][word]
        if b:
            string += 'b' + str(b)
        
        i = pageDic["info"][word]
        if i:
            string += 'i' + str(i)

        r = pageDic["ref"][word]
        if r:
            string += 'r' + str(r)
        
        c = pageDic["cat"][word]
        if c:
            string += 'c' + str(c)
        
        l = pageDic["links"][word]
        if l:
            string += 'l' + str(l)
        
        inverted_index[word].append(string)    
    currPage += 1
    if currPage % 20000 == 0:
        offset = writeIntoFile(inverted_index, title_dic, fileCount, offset)
        indexMap = defaultdict(list)
        title_dic = {}
        fileCount += 1


def mergeFiles(fileCount):

    words = {}
    files = {}
    top = {}
    flag = [0] * fileCount
    data = defaultdict(list)
    heap = []
    finalCount = 0
    offsetSize = 0

    for i in range(fileCount):
        filename = '../data/index' + str(i) + '.txt'
        files[i] = open(filename, 'r')
        flag[i] = 1
        top[i] = files[i].readline().strip()
        words[i] = top[i].split()
        print(i)
        if words[i][0] not in heap:
            heapq.heappush(heap, words[i][0])

    count = 0
    while any(flag) == 1:
        temp = heapq.heappop(heap)
        count += 1
        # print(count)
        if count % 100000 == 0:
            oldFileCount = finalCount
            finalCount, offsetSize = writeFinalIndex(data, finalCount, offsetSize)
            if oldFileCount != finalCount:
                data = defaultdict(list)
        for i in range(fileCount):
            if flag[i]:
                if words[i][0] == temp:
                    data[temp].extend(words[i][1:])
                    top[i] = files[i].readline().strip()
                    if top[i] == '':
                        flag[i] = 0
                        files[i].close()
                        # os.remove('../data/index' + str(i) + '.txt')
                    else:
                        words[i] = top[i].split()
                        if words[i][0] not in heap:
                            heapq.heappush(heap, words[i][0])
                        
    finalCount, offsetSize = writeFinalIndex(data, finalCount, offsetSize)

def writeFinalIndex(data, finalCount, offsetSize):

    title = defaultdict(dict)
    body = defaultdict(dict)
    info = defaultdict(dict)
    category = defaultdict(dict)
    link = defaultdict(dict)
    reference = defaultdict(dict)
    distinctWords = []
    offset = []

    for key in tqdm(sorted(data.keys())):
        docs = data[key]
        temp = []
        
        for i in range(len(docs)):
            posting = docs[i]
            docID = re.sub(r'.*d([0-9]*).*', r'\1', posting)
            
            temp = re.sub(r'.*t([0-9]*).*', r'\1', posting)
            if temp != posting:
                title[key][docID] = float(temp)
            
            temp = re.sub(r'.*b([0-9]*).*', r'\1', posting)
            if temp != posting:
                body[key][docID] = float(temp)

            temp = re.sub(r'.*i([0-9]*).*', r'\1', posting)
            if temp != posting:
                info[key][docID] = float(temp)

            temp = re.sub(r'.*c([0-9]*).*', r'\1', posting)
            if temp != posting:
                category[key][docID] = float(temp)

            temp = re.sub(r'.*l([0-9]*).*', r'\1', posting)
            if temp != posting:
                link[key][docID] = float(temp)
            
            temp = re.sub(r'.*r([0-9]*).*', r'\1', posting)
            if temp != posting:
                reference[key][docID] = float(temp)

        string = key + ' ' + str(finalCount) + ' ' + str(len(docs))
        distinctWords.append(string)
        offset.append(str(offsetSize))
        offsetSize += len(string) + 1

    titleData = []
    titleOffset = []
    prevTitle = 0

    bodyData = []
    bodyOffset = []
    prevBody = 0
    
    infoData = []
    infoOffset = []
    prevInfo = 0
    
    linkData = []
    linkOffset = []
    prevLink = 0
    
    categoryData = []
    categoryOffset = []
    prevCategory = 0
    
    referenceOffset = []
    referenceData = []
    prevReference = 0

    for key in tqdm(sorted(data.keys())):

        if key in title:
            string = key + ' '
            docs = title[key]
            docs = sorted(docs, key = docs.get, reverse=True)
            for doc in docs:
                string += doc + ' ' + str(title[key][doc]) + ' '
            titleOffset.append(str(prevTitle) + ' ' + str(len(docs)))
            prevTitle += len(string) + 1
            titleData.append(string)

        if key in body:
            string = key + ' '
            docs = body[key]
            docs = sorted(docs, key = docs.get, reverse=True)
            for doc in docs:
                string += doc + ' ' + str(body[key][doc]) + ' '
            bodyOffset.append(str(prevBody) + ' ' + str(len(docs)))
            prevBody += len(string) + 1
            bodyData.append(string)

        if key in info:
            string = key + ' '
            docs = info[key]
            docs = sorted(docs, key = docs.get, reverse=True)
            for doc in docs:
                string += doc + ' ' + str(info[key][doc]) + ' '
            infoOffset.append(str(prevInfo) + ' ' + str(len(docs)))
            prevInfo += len(string) + 1
            infoData.append(string)

        if key in category:
            string = key + ' '
            docs = category[key]
            docs = sorted(docs, key = docs.get, reverse=True)
            for doc in docs:
                string += doc + ' ' + str(category[key][doc]) + ' '
            categoryOffset.append(str(prevCategory) + ' ' + str(len(docs)))
            prevCategory += len(string) + 1
            categoryData.append(string)

        if key in link:
            string = key + ' '
            docs = link[key]
            docs = sorted(docs, key = docs.get, reverse=True)
            for doc in docs:
                string += doc + ' ' + str(link[key][doc]) + ' '
            linkOffset.append(str(prevLink) + ' ' + str(len(docs)))
            prevLink += len(string) + 1
            linkData.append(string)

        if key in reference:
            string = key + ' '
            docs = reference[key]
            docs = sorted(docs, key = docs.get, reverse=True)
            for doc in docs:
                string += doc + ' ' + str(reference[key][doc]) + ' '
            referenceOffset.append(str(prevReference) + ' ' + str(len(docs)))
            prevReference += len(string) + 1
            referenceData.append(string)

    thread = []
    
    thread.append(writeThread('t', titleData, titleOffset, finalCount))
    thread.append(writeThread('b', bodyData, bodyOffset, finalCount))
    thread.append(writeThread('i', infoData, infoOffset, finalCount))
    thread.append(writeThread('c', categoryData, categoryOffset, finalCount))
    thread.append(writeThread('l', linkData, linkOffset, finalCount))
    thread.append(writeThread('r', referenceData, referenceOffset, finalCount))

    for i in range(6):
        thread[i].start()

    for i in range(6):
        thread[i].join()

    with open('../data/vocab.txt', 'a') as f:
        f.write('\n'.join(distinctWords))
        f.write('\n')

    with open('../data/offset.txt', 'a') as f:
        f.write('\n'.join(offset))
        f.write('\n')

    return finalCount+1, offsetSize


def writeIntoFile(index, dictID, fileCount, titleOffset):

    # print("yo")
    prevTitleOffset = titleOffset
    data = []
    for key in sorted(index.keys()):
        string = key + ' '
        postings = index[key]
        string += ' '.join(postings)
        data.append(string)

    filename = '../data/index' + str(fileCount) + '.txt'
    with open(filename, 'w') as f:
        f.write('\n'.join(data))

    data = []
    dataOffset = []
    for key in sorted(dictID):
        temp = str(key) + ' ' + dictID[key].strip()
        data.append(temp)
        dataOffset.append(str(prevTitleOffset))
        prevTitleOffset += len(temp) + 1

    filename = '../data/title.txt'
    with open(filename, 'a') as f:
        f.write('\n'.join(data))
        f.write('\n')
    
    filename = '../data/titleOffset.txt'
    with open(filename, 'a') as f:
        f.write('\n'.join(dataOffset))
        f.write('\n')

    return prevTitleOffset



def stemming(text):
    return stemmer.stemWords(text)

def tokenization(data):

    data = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', data)
    data = re.sub(r'http[^\ ]*\ ', r' ', data)
    data = re.sub(r'\—|\%|\$|\'|\||\.|\*|\[|\]|\:|\;|\,|\{|\}|\(|\)|\=|\+|\-|\_|\#|\!|\`|\"|\?|\/|\>|\<|\&|\\|\n', r' ', data)
    return data.split()


def removeStopwords(text):
    return [x for x in text if x not in stop_words]

def processTitle(title):
    
    title_dic[currPage] = title
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
    text = text.strip()
    text = text.lower()
    text = text.replace("== references ==", "==references==")
    text = text.split("==references==")
    title = title.encode("ascii", errors="ignore").decode()
    title = title.strip()
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


class writeThread(threading.Thread):

    def __init__(self, field, data, offset, count):

        threading.Thread.__init__(self)
        self.field = field
        self.data = data
        self.count = count
        self.offset = offset

    def run(self):

        filename = '../data/' + self.field + str(self.count) + '.txt'
        with open(filename, 'w') as f:
            f.write('\n'.join(self.data))
        
        filename = '../data/offset_' + self.field + str(self.count) + '.txt'
        with open(filename, 'w') as f:
            f.write('\n'.join(self.offset))


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
            dic = {"title": title, "body": body, "info": info, "cat": cat, "links": links, "ref": ref}
            Indexing(dic)
            self.tag = ""
            self.title = ""
            self.text = ""
  


def Parser(filename):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    textExtractor = docHandler()
    parser.setContentHandler(textExtractor)
    parser.parse(filename)


if __name__ == "__main__":
    Parser(sys.argv[1])
    # inverted_index = {"inverted_index": inverted_index}
    # folder = sys.argv[2]
    offset = writeIntoFile(inverted_index, title_dic, fileCount, offset)
    with open('../data/fileNumbers.txt', 'w') as f:
        f.write(str(currPage))

    indexMap = defaultdict(list)
    title_dic = {}
    fileCount += 1
    mergeFiles(fileCount)
    # with open(folder + "/inverted_index.txt", "w+") as file:
    #     file.write(json.dumps(inverted_index))
    # with open(folder + "/title.txt", "w+") as file:
    #     file.write(json.dumps(title_dic))
