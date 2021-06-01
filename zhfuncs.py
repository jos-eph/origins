# Some functions for processing Chinese characters

import unicodedata

sampleText = "安 appears as a character in 322 words.  全全全全全 熱門服 but abc"
def unicodetest(text = sampleText):

    for char in text:
        print("Char in unicodetest: ",char)
        print("dict: ",unicodedata.__dict__)
        for funcName, valF in unicodedata.__dict__.items():
            if callable(valF) and funcName not in ["normalize","is_normalized"] and 'type' not in str(type(valF)):
                try:
                    print("Function ",funcName,"on the char: ",valF(char))
                except Exception as e:
                    print("Could not execute ",funcName,": ",e)


def isCJK(char):
    truthOfCJK = False

    try:
        truthOfCJK = ("CJK" in unicodedata.name(char))
    except Exception as e:
        print("Could not test char ",char,"! Exception\t",e,". However, execution will continue.")

    return truthOfCJK

def CJKset(scanText = sampleText):
    returnSet = set()

    for char in scanText:
        returnSet.add(char) if (isCJK(char)) else None

    return returnSet

def anyCJK(textToScan):
    CJKs = CJKset(textToScan)
    if len(CJKs) > 0: return True
    else: return False
