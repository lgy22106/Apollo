#######################
# Spell correct logic #
#######################

import re
from data import *
#enchance: more probability to the character replacement of the similar sounding character
#enchance: or map the keyboard, consider the distance between the surrounding keys

class ErrorModel:
    """
    >>> known = Counter(['hi','cat','chicken','chess', 'sun', 'son', 'son'])
    >>> em = ErrorModel(known)
    >>> ErrorModel.charList = 'abc'
    >>> em.splits('hi')
    [('', 'hi'), ('h', 'i'), ('hi', '')]
    >>> pairs = em.splits('hi')
    >>> em.getAllInserts(pairs)
    ['ahi', 'bhi', 'chi', 'hai', 'hbi', 'hci', 'hia', 'hib', 'hic']
    >>> em.getAllDeletes(pairs)
    ['i', 'h']
    >>> em.getAllTransposes(pairs)
    ['ih']
    >>> em.getAllReplacements(pairs)
    ['ai', 'bi', 'ci', 'ha', 'hb', 'hc']
    >>> em.edit1('sin')
    son

    """

    charList = 'abcdefghijklmnopqrstuvwxyz'


    def __init__(self, known):
        self.known = known





    def splits(self, word):
        """a helper function that allows edits1 to iterate through
        """
        
        #split into a list of (first, rest) for all possibility
        return [(word[:i], word[i:]) for i in range(len(word) + 1)]

    def getAllInserts(self, pairs):
        return [a + c + b for a, b in pairs for c in self.charList]

    def getAllDeletes(self, pairs):
        """
        if b is not '' condition:
            in pair ('hi', ''), 
            delete list would contain 'hi' when b is ''
            hence the need for this condition

        BUG: if pairs = ('', 'h') and ('h', '')
        will return ['']
        For single character might cause problem?
        """
        return [a + b[1:] for a, b in pairs if b is not '']

    def getAllTransposes(self, pairs):
        """
        if a is not '' and b is not '' condition:
            without the condition, ('', 'hi') and ('hi', '')
            would give 'hi' both times

        """
        return [a[:-1] + b[0] + a[-1] + b[1:] for a, b in pairs if a is not '' and b is not '']

    def getAllReplacements(self, pairs):
        """
        if b is not '' condition:
            given ('hi', '')
            would give 'hia', 'hib', etc, which is not 
            replacement, but insertion
        """
        return [a + c + b[1:] for a, b in pairs for c in self.charList if b is not '']

    def edit(self, word):
        """
        if n is len(word)
        then:
            pairs is n + 1
            inserts is (n + 1) * 26
            deletes is n
            transposes is n - 1
            replacement is n * 26
        so:
            len of total <= 54n + 25
        """
        pairs = self.splits(word)

        addList = self.getAllInserts(pairs)
        subList = self.getAllDeletes(pairs)
        swapList = self.getAllTransposes(pairs)
        editList = self.getAllReplacements(pairs)

        #set only has unique elements
        return set(addList + subList + swapList + editList)

    def getEdits(self, words, distance = 1):

        if distance == 0:
            return words
        #new set
        newSet = set()
        for word in words:
            newSet = newSet.union(self.edit(word))
        
        return set(self.getEdits(newSet, distance - 1))
    
    def filterEdits(self, edits):
        """
        filters all possible edits into known words
        """
        return filter(self.known.getCount, edits)

    def edit0(self, word):
        return set(self.filterEdits(self.getEdits((word,), 0)))
    def edit1(self, word):
        return set(self.filterEdits(self.getEdits((word,), 1)))
    def edit2(self, word):
        return set(self.filterEdits(self.getEdits((word,), 2)))

    def getBestCorrections(self, word):
        if len(self.edit0(word)) != 0:
            return self.edit0(word)
        elif len(self.edit1(word)) != 0:
            return self.edit1(word)
        elif len(self.edit2(word)) != 0:
            return self.edit2(word)
        return {word}

    def correct(self, word):
        """
        assume shorter distance model:
        edit0 > edit1 > edit2 > original word
        after filter, pick the non empty set that's minimal distance
        """
        bestCorrections = self.getBestCorrections(word)

        return max(bestCorrections, key = self.known.getCount)
    def spellcorrect(self, sentense):

        return list(map(self.correct, Util.tokenize(sentense)))

