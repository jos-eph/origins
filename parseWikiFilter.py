# Gen 2 tool--command-line utility
# called by the parseWiki tool

import zhfuncs
import wikitextparser as wtp
wtpType = type(wtp.parse("sampleWikiText"))
stringType= type("sample string")
#################################################

def shouldParseWikiBasedOnTitle(onePageDict): # key is the page name; value is the wikitext
    pageTitle=next(iter(onePageDict)) # the dict only has one entry, so next+iter retrieves the only key
    if not zhfuncs.isCJK(pageTitle[0]):
        return False # page must start with a # CJK character
    if len(pageTitle)==1 or ((pageTitle[0]+"/derived terms")==pageTitle): # single CJK character
        return True
    return False

def wtpReturnFirstSection(wtpWikitext, sectionName):
    if type(wtpWikitext) == type(None):
        return None # allows wtpReturnFirstSection to call itself without problems if there are no results

    calledType = type(wtpWikitext)

    if calledType==stringType:
        wtpWikitext = wtp.parse(wtpWikitext) # hopefully, catch and fix any not wtp arguments here

    if not isinstance(wtpWikitext,wtpType):
        raise Exception("wtpReturnFirstSection not passed a string or wikitextparser object; in fact, the type was ",type(wtpWikitext))

    parsedSections = wtpWikitext.sections

    for section in parsedSections:
        if section.title == sectionName:
            return section

    return None


def desiredSectionOfWikitext(onePageDict):
    pageTitle=next(iter(onePageDict)) # the dict only has one entry, so next+iter retrieves the only key
    chineseSection = wtpReturnFirstSection(onePageDict[pageTitle],"Chinese")
    if chineseSection is None:
        return None
    else:
        return {pageTitle : str(chineseSection)}