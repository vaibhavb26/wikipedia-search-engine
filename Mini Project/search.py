import re
import json
import sys
import os
from index import stemming, tokenization, removeStopwords
from collections import defaultdict
from collections import Counter


inverted_index = defaultdict(list)
title = {}
def read_file(testfile):

    with open(testfile, 'r') as file:
        queries = file.readlines()
    return queries


def write_file(outputs, path_to_output):

    with open(path_to_output, 'w+') as file:
        # print(outputs)
        for output in outputs:
            for line in output:
                file.write(line.strip() + '\n')
            file.write('\n')


def search(path_to_index, queries):
    
    output = []
    for query in queries:
        # print(query)
        answer = []
        query = query.lower()
        if re.match(r'title|body|infobox|category|ref|link:', query):
            query = query.split(" ")
            doc_list = []
            for token in query:
                token = token.split(":")
                stemmed_token = stemming(token)
                word = stemmed_token[1]
                # print(word)
                # print(token[0])
                if "body" == token[0]:
                    for x in inverted_index[word]:
                        if 'b' in x:
                            doc_list.append(re.split('b|t|r|c|l|i', x)[0])
                if "title" == token[0]:
                    for x in inverted_index[word]:
                        if 't' in x:
                            doc_list.append(re.split('b|t|r|c|l|i', x)[0])
                if "infobox" == token[0]:
                    for x in inverted_index[word]:
                        if 'i' in x:
                            doc_list.append(re.split('b|t|r|c|l|i', x)[0])
                if "category" == token[0]:
                    for x in inverted_index[word]:
                        if 'c' in x:
                            doc_list.append(re.split('b|t|r|c|l|i', x)[0])
                if "ref" == token[0]:
                    for x in inverted_index[word]:
                        if 'r' in x:
                            doc_list.append(re.split('b|t|r|c|l|i', x)[0])
                if "link" == token[0]:
                    for x in inverted_index[word]:
                        if 'l' in x:
                            doc_list.append(re.split('b|t|r|c|l|i', x)[0])
            # print(doc_list)
        else:
            tokens = tokenization(query)
            tokens = removeStopwords(tokens)
            tokens = stemming(tokens)
            doc_list = []
            for token in tokens:
                # print(token)
                for x in inverted_index[token]:
                    doc_list.append(re.split('b|t|r|c|l|i', x)[0])
        result = Counter(doc_list)
        sorted_result = sorted(result.items(), key = lambda kv:kv[1], reverse = True)
        # print(sorted_result)
        i = 0;
        for key, value in sorted_result:
            # print(title[key])
            answer.append(title[key])
            i += 1
            if i == 10:
                break
        output.append(answer)
    return output


def main():
    global inverted_index
    global title
    path_to_index = sys.argv[1]
    testfile = sys.argv[2]
    path_to_output = sys.argv[3]
    with open(os.path.join(path_to_index, 'inverted_index.txt')) as f:
        inverted_index = defaultdict(list, json.load(f)['inverted_index'])

    with open(os.path.join(path_to_index, 'title.txt')) as t:
        title = json.load(t)

    queries = read_file(testfile)
    outputs = search(path_to_index, queries)
    write_file(outputs, path_to_output)


if __name__ == '__main__':
    main()
