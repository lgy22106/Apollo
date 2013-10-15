from data import *
from spellcorrect import *
import operator




def getData(n):
    """
    """
    files = ("http://norvig.com/big.txt",)
    fc = FileConnector(files)
    dp = DataProvider(fc)
    p1 = dp.getProbability(n)

    return p1

known = getData(1)

def correct(s):
    em = ErrorModel(known)
    return em.spellcorrect(s)