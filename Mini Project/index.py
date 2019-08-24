import sys
import operator
from collections import defaultdict
import timeit
import re
import os
import pdb
import xml.sax
from nltk.corpus import stopwords
from nltk.stem.porter import *
import Stemmer
import threading
from unidecode import unidecode
from tqdm import tqdm


class docHandler(xml.sax.ContentHandler):

    def __init__(self):
        self.tag = ''
        self.title = ''
        self.text = ''
        self.id = ''

    def startElement(self, tag, attr):
        self.tag = tag

    def endElement(self, tag):
        if tag == 'page':
            print(self.text, self.title)

class Parser():
    def __init__(self, filename):
        self.parser = xml.sax.make_parser()
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        self.textExtractor = docHandler()
        self.parser.setContentHandler(self.textExtractor)
        self.parser.parse(filename)

if __name__ == "__main__":
    parser = Parser(sys.argv[1])