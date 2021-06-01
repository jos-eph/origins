#!/usr/bin/env python3
# Gen 2 tool--command-line utility.

# parseWiki is a command-line tool to process a larger Wiktionary Wikimedia file into
# json output which will contain only the subset of pages that we find interesting.
# Initial XML extraction written with the help of https://towardsdatascience.com/wikipedia-data-science-working-with-the-worlds-largest-encyclopedia-c08efbac5f5c

import argparse
argParser = argparse.ArgumentParser()
argParser.add_argument("wiki_file_to_parse", help="A Wikimedia file, either in bz2 or xml format")
argParser.add_argument("--output-file",help="Path of the JSON file which will contain \
a dictionary of processed pages with the page title as the key.") # args.output_file
args = argParser.parse_args()


#################################################################################

import xml.sax
import sys
sys.tracebacklimit=0 # suppress traceback messages; report exceptions as the program raises them
import gzip, bz2
import json

from parseWikiFilter import shouldParseWikiBasedOnTitle, desiredSectionOfWikitext

def errorPrint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

from datetime import datetime

def printNow():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)

#################################################################################
# WikiXMLHandler.popWiki() returns a dict in the form {'<actualtitle>' : '<actualText' }
# in other words, the dict does not have a key named 'title'

__joinChar__ = '' # if you insert a space, it will confuse the parser

class WikiXmlHandler(xml.sax.handler.ContentHandler): # initialized for convenience following

    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []

        self.totalPages  = 0
        self.pagesPopped = 0

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name in ('title', 'text'):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            self._values[name] = __joinChar__.join(self._buffer) # reset for every tag

        if name == 'page':
            self.totalPages += 1
            self._pages.append({self._values['title'] : self._values['text']})

    def canPop(self):
        return (len(self._pages) >= 1)

    def popWiki(self):
        if self.canPop():
            self.pagesPopped += 1
            return self._pages.pop()
        else:
            raise

#        ******* Necessary shorthand init *******           #

xmlParser = xml.sax.make_parser()
xmlHandler = WikiXmlHandler()
xmlParser.setContentHandler(xmlHandler)

#################################################################################

inputFileName = args.wiki_file_to_parse
fileExtension = inputFileName.split('.')[-1]

if fileExtension not in ['xml','gz','bz2']:
    raise Exception(fileExtension + " is not a supported filetype for file " + inputFileName + ".")

try:
    readMode="r"
    if fileExtension == "xml":
        wikiTextFile = open(inputFileName,readMode)
    elif fileExtension == "gz":
        wikiTextFile = gzip.open(inputFileName,readMode)
    elif fileExtension == "bz2":
        wikiTextFile = bz2.open(inputFileName,readMode)
except Exception as e:
    raise
######################################################################################
############################# Main program logic                    ##################

pageDict = {}
i = 0
j = 0

printNow()
for fileLine in wikiTextFile:
    xmlParser.feed(fileLine)
    if xmlHandler.canPop():
        oneWikiTitleAndWikitext = xmlHandler.popWiki()
        if shouldParseWikiBasedOnTitle(oneWikiTitleAndWikitext):
            desiredPageExcerpt = desiredSectionOfWikitext(oneWikiTitleAndWikitext)
            if desiredPageExcerpt is not None:
                pageDict.update(desiredPageExcerpt)
                j += 1

    i += 1
    # errorPrint("line ",i,"\t\tTotal count = ",j)
    if (i % 10000)==0 and i!=0:
        errorPrint("****\t",i," lines processed; char count is \t",j)

print("...Final line count:\t",i,"\tchar count: \t",j)
printNow()

try:
    wikiTextFile.close()
except Exception as e:
    raise

if not args.output_file:
    outputFileName = "pageDict.json"
else:
    outputFileName = args.output_file

try:
    writeMode="w"
    fWriteFile = open(outputFileName,writeMode)
    json.dump(pageDict,fWriteFile,indent=10,separators=(',\n','\n: '))
    fWriteFile.close()
except Exception as e:
    raise

#######################################################################################
