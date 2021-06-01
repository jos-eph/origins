#!/usr/bin/env python3
# Gen 2 tool--command-line utility.

# pullRelationships is a command-line tool that processes a json file containing a dictionary of wiktionary pages
# and returns the resulting relationships among Chinese characters as a json file.

import argparse
argParser = argparse.ArgumentParser()
argParser.add_argument("pageDict", help="A JSON file, containing a dictionary of pages where \
the key is the title of the page and the entry is wikitext.")
argParser.add_argument("--output-file",help="Path of the JSON file which will contain \
the processed relationships.") # args.output_file
args = argParser.parse_args()

inputFileName = args.pageDict
if not args.output_file:
    outputFileName = "relationships.json"
else:
    outputFileName=args.output_file
    fileExtension = outputFileName.split('.')[-1]
    if (fileExtension.lower() != "json"):
        outputFileName += ".json"

####
from pprint import pprint as pretty


#############################################################################

import json
import wikitextparser as wtp

readMode = "r"
writeMode = "w"

import sys
sys.tracebacklimit=0 # suppress traceback messages; report exceptions as the program raises them

import wikitextparser as wtp

from pullRelationshipsFilter import RelationshipsFilter
##############################################################################

# This converts the type of dicts that the program uses to a JSON-friendly format, with lists instead of sets.
def dictWithSetValueEntriesToList(dictionaryWithValuesAsSets):

    if type(dictionaryWithValuesAsSets) is not dict:
        raise Exception("dictWithSetValueEntriesToList expects a dictionary.")
    newDict = {}
    for key,setValue in dictionaryWithValuesAsSets.items():
        if type(setValue) is not set:
            raise Exception("One of this dictionary's values was not of type set.")
        newDict.update({key : list(setValue)})

    return newDict

##############################################################################

try:
    fReadFile=open(inputFileName,readMode)
    pageDict=json.load(fReadFile)
except Exception as e:
    raise

Relationships = RelationshipsFilter()
jsonFriendlyOutputDict = {}

i = 0
for pageTitle, wikiText in pageDict.items():
    print("\t\t\t\tPAGE: ",i,"\t\t",pageTitle)
    parsed = wtp.parse(wikiText)
    templates = parsed.templates
    for template in templates:
        Relationships.trackTemplate(pageTitle, template)

    pageRelationships = Relationships.donePage(pageTitle)
    pretty(pageRelationships)

    if pageRelationships is not None:
        updateDict = {pageTitle : dictWithSetValueEntriesToList(pageRelationships)}
        jsonFriendlyOutputDict.update({pageTitle: dictWithSetValueEntriesToList(pageRelationships)})

    i += 1
    print("****************************************")

try:
    fWriteFile = open(outputFileName,'w')
    json.dump(jsonFriendlyOutputDict,fWriteFile,indent=10,separators=(',\n','\n: '))
    fWriteFile.close()
except Exception as e:
    raise
