########################################################
# Different abstraction and manipulation of words data #
########################################################

import urllib.request
import re
import operator
from collections import Counter

class Util:
    @staticmethod
    def tokenize(text):
        """tokenize all words in text
        BUG: consider the word patrick's will become [patrick, s]
        need to firgure out how to consider ' into words
        """
        return re.findall(r"[a-z]+", text)

class FileConnector:
    """File Connector that parses files, provide data to data provider
    attributes:
        files(tuple of files in both url and/or local paths)
    notes:
        assuming file connector is static, meaning once the files are loaded, it cannot be removed. enhancement later?

    >>> fc = FileConnector(("http://www.gutenberg.org/cache/epub/100/pg100.txt","D:\Work\Apollo\data\shakespeare.txt"))
    >>> fc.isWebUrl("http://google.com")
    True
    >>> fc.isWebUrl("D:\ipython")
    False
    >>> fc.tokenize("haha wor.ld hello man! this is great")
    ['haha', 'wor', 'ld', 'hello', 'man', 'this', 'is', 'great']
    """

    def __init__(self, files = ()):
        self.files = files

    def getData(self):
        tokens = []
        for path in self.files:
            t = self.parseFile(path)
            tokens.extend(t)
        return tokens

    def parseFile(self, path):
        text = self.getFile(path)
        t = Util.tokenize(text)
        return t
        

    def getFile(self, path):
        if self.isWebUrl(path):
            return self.readWebFile(path)
        return self.readLocalFile(path)

    def readWebFile(self, path, encode = 'utf-8'):
        response = urllib.request.urlopen(path)
        data = response.read()
        text = data.decode(encode)
        return text

    def readLocalFile(self, path, encode = 'utf-8'):
        with open(path, 'r', encoding = encode) as f:
            text = f.read()
        return text

    def isWebUrl(self, path):
        """check if uri contains "http://"
        BUG: if any local path contains http, it will treat as a url
        """
        return "http://" in path


class MongoConnector:
    """Mongo data connector
    @TODO
    """
    def __init__(self, db, user, password, port):
        self.db = db
        self.user = user
        self.password = password
        self.port = port

    def getData(self):
        return 'hi'


class GenericConnector:
    """a interface for different data connectors"""

    def __init__(self):
        print("interface")


class redict(dict):
    """this class is a child of dict class that takes in a regex pattern in key
    usage:
    d = {'hello':1, 'hi': 2}
    rd = redict(d)
    for k, v in rd[r"[a-z]+"]:
        print(k, v)

    note: redict O(n) is slower than dict O(ln(n)) class. 
    """
    def __init__(self, d):
        """calling super constructor of dict"""
        dict.__init__(self, d)
    def __getitem__(self, regex):
        """generator function creates an iterator"""
        pattern = re.compile(regex)
        ks = filter(pattern.match, self.keys())

        #returns a tuple of (key, value)
        for k in ks:
            yield (k, dict.__getitem__(self, k))



class NgramCharCreator:
    def __init__(self):
        print("TODO")



class NgramWordCreator:
    """Creates ngram files
    ex: hello this is world
    1-gram file:
    hello
    this
    is
    world
    2-gram file:
    hello this
    this is
    is world
    3-gram file:
    hello this is
    this is world

    attributes:
        tokens
    """

    def __init__(self, tokens):
        self.tokens = tokens

    def getNgram(self, n):
        """returns a list of ngram from tokens
        handle extreme case: index out of bounce at the last items
        """
        ngramList = []
        for i in range(len(self.tokens) - n):
            ngramList.append(self.getNgramEntry(i, i + n))
        return ngramList

    def getNgramEntry(self, start, end):
        return ' '.join(self.tokens[start:end])




class DataProvider:
    """ DataProvider is the main interface for data manipulation of words.
    attributes:
        connector
        ngram
    """
    def __init__(self, connector):
        self.connector = connector
        self.ngram = NgramWordCreator(self.connector.getData())


    def getCounter(self, n):
        return Counter(self.ngram.getNgram(n))

    def getProbability(self, n):
        return Probability(Counter(self.ngram.getNgram(n)))

class Probability:
    """ Probability class is a wrapper of the Counter object.
    Contains logic implementations using Counter
    attributes:
        counter(Counter)
        size
    """

    def __init__(self, counter):
        assert len(counter) != 0, 'counter cannot be empty'
        self.counter = counter
        #pre compute length
        self.size = len(self.counter)

    def __getitem__(self, key):
        return self.getCount(key)


    def getCounter(self):
        return self.counter

    def getCount(self, word, default = 0):
        """
        smoothing: assume that we have seen all possible words at least once
        since the data is not infinte, we cannot assume one correct word is 
        not a word.
        therefore, we set a default value to 1
        """
        return self.counter.get(word, default)

    def getP(self, word, default = 0):
        return self.getCount(word, default) / self.size

    def getMostCommon(self, regex, n):
        rd = redict(self.counter)
        unsortedList = [pair for pair in rd[regex]]
        sortedList = sorted(unsortedList, key = lambda pair: pair[1], reverse = True)

        return sortedList[:n]






