# Second generation of an earlier tool-- now a command-line utility
# library file called by pullRelationships

__sameST__ = "same simplified and traditional"
__simplified__ = "simplified character"
__alternateSimplified__ = "lesser-used alternate simplified character"
__traditional__ = "traditional character"
__alternateTraditional__ = "lesser-used alternate traditional character"
__overflow__ = "__overflow__" # for an overflow dictionary
__ideogram__ = "ideogram"
__ideogrammicCompound__ = "ideogrammatic compound"
__psc__                 = "phono-semantic compound"
__pictogram__ = "pictogram"

import wikitextparser as wtp
wtpTemplateType = type(wtp.parse("{{Han compound|糸|t1=thread|各|ls=psc|c1=s|c2=p}}").templates[0])

import simpletotrad # a simple table of simplified characters and their traditional equivalent, called by a Lua macro in actual Wiktionary pages as a default for certain macros and included here for completeness

##################################################################################

class RelationshipsFilter():

    permitted = ['zh-forms','zh-see','Han compound','Han_compound','Han simp','liushu','see derivation subpage',
                 'zh-etym-triple','zh-etym-double','zh-etym-quadruple','zh-eytm-sextuple','zh-etym-sextuple',
                 'zh-etym-quintuple','zh-alt-form'] # these are all templates we might consider processing down the line

    processedSynonyms = [ ["zh-see"],["zh-forms"],["Han simp"],["Han compound","Han_compound"],["liushu"]
                          ]# these are templates we are currently processing. item 0 is the preferred name

    pageTemplateValueDict = {}

    characterAnalysisDict = {}


    # Given a pageName (equivalent to a single character) and wikitextparser template object containing a template
    # on that page, stores an individual template in a dictionary within the object where each key represents a single
    # page (character). When we are done stuffing template data into the object, we call
    # RelationshipsFilter.donePage(pageTitle) to have the object analyze templates on that page.

    def trackTemplate(self, pageName, template):
        standardizedPermittedTemplateName = self._processedTemplateMainSpelling(template)
        if not standardizedPermittedTemplateName:
            return None

        if not self.permittedToAnalyzeTemplates(pageName): # if not a character; if, e.g., "東/derived terms"
            return None

        templateDict = self.templateToDict(template,standardizedName=standardizedPermittedTemplateName)
        templateName = next(iter(templateDict)) # this is a single-key dictionary, so we are grabbing the only key name

        if pageName not in self.pageTemplateValueDict.keys():
            self.pageTemplateValueDict[pageName] = {'pulledTemplates' : True}

        if templateName not in self.pageTemplateValueDict[pageName]:
            self.pageTemplateValueDict[pageName].update(templateDict) # but what happens, with e.g. 冈, if there is more than one use of a template, like zh-see?
        else:
            self._updateOverflow(self.pageTemplateValueDict[pageName],templateDict)


    # This externally visible method exposes functionality for analyzing a page containing character templates when
    # we are done processing the template.
    # Essentially, it is a safe way to call RelationshipsFilter._initialPageProcess(pageName), and
    # easily calls up the pageTemplateValueDict associated with a particular pageName.

    def donePage(self, pageName):
        if not self.permittedToAnalyzeTemplates(pageName):
            return None

        if pageName not in self.characterAnalysisDict.keys():
            self.characterAnalysisDict[pageName] = {}

        if pageName not in self.pageTemplateValueDict.keys():
            self.pageTemplateValueDict[pageName] = {'pulledTemplates' : False}

        thisPage = self.pageTemplateValueDict[pageName]

        self._initialPageProcess(pageName, thisPage)

        return self.characterAnalysisDict[pageName]


    # This is the meat and potatoes, and calls one safe processor method for each template we want to process.
    def _initialPageProcess(self, pageName, onePageTemplates):
        self._handleZhForms(pageName, onePageTemplates)
        self._handleZhSee(pageName, onePageTemplates)
        self._handleHanSimp(pageName,onePageTemplates)
        self._handleHanCompound(pageName, onePageTemplates)
        self._handleLiuShu(pageName,onePageTemplates)


    # This tag has information on which characters are put together to form the character in question.
    def _handleHanCompound(self, characterWhichIsCompounded, onePageTemplates):
        if not self._testForTemplate(onePageTemplates,"Han compound"):
            return False

        # some characters, like 疑, have more than one Han compound tag. To a rough approximation, the first one is the right one and we will ignore the overflow.
        paramList = ["c","t"]
        liushuDict = {'i': __ideogram__, 'ic':__ideogrammicCompound__, 'psc':__psc__}
        HanCompoundArgsDict = self._grabPrincipalTemplateDict(onePageTemplates,"Han compound") # assumes only one of these tags per page
        argumentValueTupleList = self._allValuesTupleListForNumberedArguments(paramList,HanCompoundArgsDict)

        if "ls" in HanCompoundArgsDict:
            if HanCompoundArgsDict["ls"] in liushuDict: # Test to see if the argument values are something we actually process.
                self._addPropertyToSetOfCharacter(characterWhichIsCompounded,"compoundType",liushuDict[HanCompoundArgsDict["ls"]])

        typePosition = paramList.index("c") + 1 # the first position in the tuple will be the source character, so we increase by one. We use paramList.index("c") so the list can change and it isn't hard-coded.
        translationPosition = paramList.index("t") + 1 # ditto

        for argumentTuple in argumentValueTupleList:
            componentCharacter = argumentTuple[0]
            typeOfComponent=argumentTuple[typePosition]
            translation=argumentTuple[translationPosition]
            self._binaryPropertySet((characterWhichIsCompounded, componentCharacter),("hasComponent","isComponentOf"))
            if translation is not None:
                self._addPropertyToSetOfCharacter(componentCharacter,"translation",translation)
            if typeOfComponent=="s":
                self._binaryPropertySet((characterWhichIsCompounded, componentCharacter), ("hasSemanticComponent","isSemanticComponentOf"))
            if typeOfComponent=="p":
                self._binaryPropertySet((characterWhichIsCompounded, componentCharacter), ("hasPhoneticComponent","isPhoneticComponentOf"))

    # The liushu tag has similar information to Han compound as far as liushu type, but does not list the actual character components.
    def _handleLiuShu(self,pageName,onePageTemplates):
        # some characters, like 丙, have more than one liushu tag. To a rough approximation, the first one is the right one and we will ignore the overflow.

        if not self._testForTemplate(onePageTemplates,"liushu"):
            return False

        liushuDict = {'p': __pictogram__, '1': __pictogram__, # unlike Han compound, liushu allows you to specify argument types by number.
                      'i': __ideogram__, '2': __ideogram__,
                      'ic':__ideogrammicCompound__, '3':__ideogrammicCompound__,
                      'psc':__psc__, '4':__psc__}

        liushuArgsDict = self._grabPrincipalTemplateDict(onePageTemplates,"liushu")

        if "1" not in liushuArgsDict: # Safety tests to make sure the template has valid data.
            return False
        else:
            liushuValue = liushuArgsDict["1"]

        if liushuValue not in liushuArgsDict:
            return False

        self._addPropertyToSetOfCharacter(pageName,"compoundType",liushuDict[liushuValue])


    # This template supplies information about alternate simplified and traditional characters.
    # This method is the first to implement an "overflowDict", recursively calling the method if passed an
    # overflowDict. Since overflow is the exception and not the rule, instead of burying values further in the
    # template dictionary, we call a separate _overflowHandle method to handle an overflow dictionary.
    def _handleZhForms(self, traditionalCharacter, templateValuesForPage, overflowDict=None):
        if not self._testForTemplate(templateValuesForPage,"zh-forms"):
            return False

        thisCharAnalysis = self._findCharAnalysisDictForChar(traditionalCharacter)

        if overflowDict is None:
            zhformsArgsDict = self._grabPrincipalTemplateDict(templateValuesForPage, "zh-forms")
        else:
            zhformsArgsDict = overflowDict

        sValues = self.collectAllTemplateArgumentValuesDedupe("s",zhformsArgsDict)
        tValues = self.collectAllTemplateArgumentValuesDedupe("t",zhformsArgsDict)

        typeSet = self._makeSureSetInDict(thisCharAnalysis,"type")

        if sValues[0] is None: # the character has the same simplified and traditional value; no |s=
            typeSet.add(__sameST__)
            mainTraditionalCharAnalysis = thisCharAnalysis
        else: # there is at least one simplified character, and it simplifies the traditional character
            mainSimplified = sValues[0]
            self._setSimplifiedAndTraditional(mainSimplified,traditionalCharacter)

        # below is for |s2, |s3, etc.
        if sValues[1] is not None: # we have alternate simplified characters
            for additionalSimplified in sValues[1]:
                self._setSimplifiedAndTraditional(additionalSimplified, traditionalCharacter,alternate=__alternateSimplified__)

        if tValues[1] is not None: # we have alternate traditional characters
            additionalTraditionalSet = self._makeSureSetInDict(thisCharAnalysis,"additionalTraditional")
            for additionalTraditional in tValues[1]:
                additionalTraditionalSet.add(additionalTraditional)
                self._setSimplifiedAndTraditional(mainSimplified,additionalTraditional,alternate=__alternateTraditional__)

        if overflowDict is None:
            self._overflowHandle(self._handleZhForms, "zh-forms", traditionalCharacter, templateValuesForPage)

        return True


    # Sometimes a zh-see tag will provide information above and beyond a simplified/traditional relationship, such as alternate
    # simplified or traditional characters.
    def _handleZhSee(self, characterOperatedOn, templateValuesForPage, overflowDict=None):
        # note that occasionally, characters, like 冈, will have more than one zh-see template
        if not self._testForTemplate(templateValuesForPage,"zh-see"):
            return False

        if overflowDict is None:
            zhseeArgsDict = self._grabPrincipalTemplateDict(templateValuesForPage, "zh-see")
        else:
            zhseeArgsDict = overflowDict

        if "3" in zhseeArgsDict: # not using this now, because some translations are in fact dialect-only
            translationOfArgOne = zhseeArgsDict["3"]
        else:
            translationOfArgOne = None

        characterResultOfOperation = zhseeArgsDict["1"]
        operationMode = zhseeArgsDict["2"] if "2" in zhseeArgsDict else "" # blank argument 2 defaults to s, but here will leave out to avoid erroneous result with e.g. 乗
        # I'd like to revisit the case of a blank ["2"] in the future
        # below if statement formerly had 'or "2" not in zhseeArgsDict

        if operationMode in ["s","simp","simplified","sv","svt"]: # the characterResultOfOperation is simplified; blank arg 2 defaults to s
            # 𫛫 - traditional
            traditionalCharacter = characterResultOfOperation
            simplifiedCharacter = characterOperatedOn

            self._setSimplifiedAndTraditional(simplifiedCharacter, traditionalCharacter)

        if overflowDict is None:
            self._overflowHandle(self._handleZhSee, "zh-see", characterOperatedOn, templateValuesForPage)

        return True



    # Han simp is another tag that provides information about simplified characters.
    # It will raise an Exception if the tag is present in a Wiktionary page but would be providing bad data.
    def _handleHanSimp(self, pageNameAndSimplifiedCharacter, templateValuesForPage, overflowDict=None ):
        # rarely, characters will use this twice. For example, 参 is a double simplification.
        if not self._testForTemplate(templateValuesForPage,"Han simp"):
            return False

        if overflowDict is None:
            hanSimpArgsDict = self._grabPrincipalTemplateDict(templateValuesForPage, "Han simp")
        else:
            hanSimpArgsDict = overflowDict

        if len(hanSimpArgsDict)==0:
            return False

        simplifiedCharacter = pageNameAndSimplifiedCharacter

        if "1" in hanSimpArgsDict:
            traditionalCharacterOrCharacters = [hanSimpArgsDict["1"]] # careful, because some pages, like 岚, have no 1 and instead get the traditional char from somewhere else
        else:
            traditionalCharacter = simpletotrad.simpleToTrad(pageNameAndSimplifiedCharacter)
            if traditionalCharacter is None:
                # raise Exception("Han simp handler is confused--there is no traditional character listed in the template and no traditional equivalent in the simplified to traditional lookup table.")
                print("Han simp handler is confused--there is no traditional character listed in the template and no traditional equivalent in the simplified to traditional lookup table.")
            else:
                traditionalCharacterOrCharacters = [traditionalCharacter]

        if "a" in hanSimpArgsDict:
            additionalTraditionalCharacterWhichIsSimplified = hanSimpArgsDict["a"]
            traditionalCharacterOrCharacters.append(additionalTraditionalCharacterWhichIsSimplified)
        else:
            additionalTraditionalCharacterWhichIsSimplified = None

        for traditionalCharacter in traditionalCharacterOrCharacters:
            self._setSimplifiedAndTraditional(simplifiedCharacter,traditionalCharacter)

        listOfSimplifiedComponents = self.correlateTuplesInTemplateArguments("f","t",hanSimpArgsDict)

        if listOfSimplifiedComponents is not None:
            for traditionalComponent,simplifiedComponent in listOfSimplifiedComponents: # assume that the components only simplify the main trad character

                if traditionalComponent is None or simplifiedComponent is None: # this shouldn't happen, but in case it does...
                    continue

                self._setSimplifiedAndTraditional(simplifiedComponent, traditionalComponent, isSimplifiedComponentOf=simplifiedCharacter,
                                                  isTraditionalComponentOf=traditionalCharacter)

        if overflowDict is None:
            self._overflowHandle(self._handleHanSimp, "Han simp", pageNameAndSimplifiedCharacter, templateValuesForPage)

        return True

    #### Utility methods called by other methods ####

    # This a refactored method to implement an operation I found myself doing over and over.
    # It itself calls refactored methods.
    def _setSimplifiedAndTraditional(self, simplifiedCharacter, traditionalCharacter,alternate=False,
                                     isSimplifiedComponentOf=None,isTraditionalComponentOf=None):

        self._binaryPropertySet( (simplifiedCharacter, traditionalCharacter), ("simplifies","simplifiedBy") )
        self._addPropertyToSetOfCharacter(simplifiedCharacter,"type",__simplified__)
        self._addPropertyToSetOfCharacter(traditionalCharacter,"type",__traditional__)

        if alternate==False:
            self._addPropertyToSetOfCharacter(traditionalCharacter,"mainSimplified",simplifiedCharacter)

        if alternate==__alternateSimplified__:
            self._addPropertyToSetOfCharacter(simplifiedCharacter,"flags",__alternateSimplified__)

        if alternate==__alternateTraditional__:
            self._addPropertyToSetOfCharacter(traditionalCharacter,"flags",__alternateTraditional__)

        if isSimplifiedComponentOf is not None:
            mainSimplified = isSimplifiedComponentOf
            self._addPropertyToSetOfCharacter(mainSimplified,"type",__simplified__)
            self._binaryPropertySet( (mainSimplified, simplifiedCharacter), ("hasComponent","isComponentOf"))

        if isTraditionalComponentOf is not None:
            mainTraditional = isTraditionalComponentOf
            self._addPropertyToSetOfCharacter(mainTraditional,"type",__traditional__)
            self._binaryPropertySet( (mainTraditional, traditionalCharacter), ("hasComponent","isComponentOf"))


    def _addPropertyToSetOfCharacter(self,character,property,value):
        characterAnalysis = self._findCharAnalysisDictForChar(character)
        propertyToSet = self._makeSureSetInDict(characterAnalysis,property)
        propertyToSet.add(value)

    def _binaryPropertySet(self, characterPair, propertyPair):
        # propertyPair, e.g. (hasComponent, isComponentOf)

        if len(characterPair) != 2 or len(propertyPair) != 2:
            raise Exception("_binaryPropertySet operates on two Characters only, with reciprocal properties")

        self._addPropertyToSetOfCharacter(characterPair[0],propertyPair[0],characterPair[1])
        self._addPropertyToSetOfCharacter(characterPair[1],propertyPair[1],characterPair[0])

    # Assumes argument names may terminate with a digit or digits,
    # but that any other digits are part of the argument name.
    # Processes argument names into a list of the form
    # [<alphabetic portion as string>, <digit portion as string>,
    # <integer conversion of digit portion>].
    # Fills position 1 or position 2 of the list with None if not present.
    def argumentNameIntSplit(self,nameOfArgument):
        if len(nameOfArgument)==0:
            raise Exception("Argument name was blank!")

        if not nameOfArgument[-1].isdigit():
            return [nameOfArgument, None, 1]

        alphabeticPortion = ""
        digitPortion = ""

        for i in range(len(nameOfArgument)-1,-1,-1):
            char = nameOfArgument[i]
            if char.isdigit():
                digitPortion = char + digitPortion
            else:
                alphabeticPortion = char + alphabeticPortion
                if lastChar.isdigit():
                    return [nameOfArgument[0:i+1],digitPortion,int(digitPortion)]
            lastChar = char

        return [alphabeticPortion, None if digitPortion=='' else digitPortion,
                int(digitPortion) if digitPortion is not None else None]


    # A utility function that converts a wikitextparser template object into
    # a dictionary, of the form
    # {'templateName' : {argument1 : <<value or list of values>>, argument2: <<value or list of values>>}}
    # All methods expect this format. It is a hedge against future API changes for wikitextparser.
    def templateToDict(self, template,standardizedName=None):
        self.testTemplateType(template)
        templateName = standardizedName if not None else template.name

        processedTemplateDict = {templateName : {} }
        argumentDict = {}
        for argument in template.arguments:
            argumentDict[argument.name] = self.processTemplateArgumentValue(argument.value)
        processedTemplateDict[template.name] = argumentDict

        return processedTemplateDict


    def testTemplateType(self, templateToTest): # throw an exception if we strictly need wikitextparser type and are not passed it
        if type(templateToTest) is not wtpTemplateType:
            raise Exception("Passed input " + str(templateToTest) + "...which is not a wikitextparser template!")
        else:
            return True

    def isPermitted(self,template): # test whether a template, passed either in string form or as a wikitextparser template, is in the permitted list
        if type(template)==wtpTemplateType:
            return template.name in self.permitted
        elif type(template) is str:
            return template in permitted
        else:
            raise Exception("Passed putative template " + str(template) + " of type " + str(type(template)) + " is neither a "
                            + " wikitextparser template nor a string!")

    def _processedTemplateMainSpelling(self,template): # accounts for variants like Han compound vs Han_compound
        if type(template)==wtpTemplateType:
            templateName = template.name
        elif type(template) is str:
            templateName = template
        else:
            raise Exception("Passed putative template " + str(template) + " of type " + str(type(template)) + " is neither a "
                            + " wikitextparser template nor a string!")

        firstLetterLowercase = templateName[0].lower()
        if len(templateName)==1:
            templateName = firstLetterLowercase
        else:
            templateName = firstLetterLowercase + templateName[1:]

        for synonymList in self.processedSynonyms:
            if templateName in synonymList or templateName[0].upper() + templateName[1:] in synonymList: # follows Wikitext conditions for validity
                return synonymList[0]

        return False


    def cat(self, template): # useful for visualizing templates arguments in a file
        self.testTemplateType(template)
        print("template: ",template)
        i = 0
        print("template name: \t",template.name)
        print("length of template.arguments: ",len(template.arguments))
        for argument in template.arguments:
            print("\targument name: ",argument.name)
            print("\t\tpython argument position starting from 0: ",i,"\n\t\t\tvalue: ",argument.value)
            i +=1
        print("\n")

    def processTemplateArgumentValue(self,argument): # some templates provide a comma-delimited list of item values; this converts them to a list.
        if "," in argument:
            return argument.split(',')
        else:
            return argument


    def catPermitted(self,template):
        if self.isPermitted(template):
            self.cat(template)

    def permittedToAnalyzeTemplates(self, pageName):
        if len(pageName) != 1:
            return False
        else:
            return True

    def _updateOverflow(self, pageTemplateValueDictForPage, templateDict):
        templateName = next(iter(templateDict))
        if __overflow__ not in pageTemplateValueDictForPage:
            pageTemplateValueDictForPage[__overflow__] = {__overflow__ : {} }
        if templateName not in pageTemplateValueDictForPage[__overflow__]:
            pageTemplateValueDictForPage[__overflow__][templateName] = []

        pageTemplateValueDictForPage[__overflow__][templateName].append(templateDict[templateName]) # the key value at templateDict[templateName] is also a dict!

    def collectAllTemplateArgumentValuesDedupe(self,root,dictionary): #assumes that a root, by itself, means the argument is used only once
        if type(root) is not str:
            raise Exception("root passed to collectAllTemplateArgumentValuesDedupe must be a string!")

        rootValue = None
        numberedArgValueSet = set()

        if root in dictionary:
            rootValue = dictionary[root]

        i = 1

        while root + str(i) in dictionary:
            numberedArgValueSet.update(dictionary[root + str(i)])
            i +=1

        returnValue = (rootValue, None if len(numberedArgValueSet)==0 else numberedArgValueSet)

        return returnValue

    def _allValuesTupleListForNumberedArguments(self,listOfStems,templateArgumentDict):
        tupleList = []
        i = 1
        while str(i) in templateArgumentDict:
            # print("...in the allValuesTupleList loop")
            candidateTuple = []
            strOfNumber = str(i)
            candidateTuple.append(templateArgumentDict[strOfNumber])
            for j in range (0,len(listOfStems)):
                if listOfStems[j] + str(i) in templateArgumentDict:
                    candidateTuple.append(str(templateArgumentDict[listOfStems[j] + str(i)])) # had to cast it as a string because, (I think), I automatically converted comma-delimited text strings to lists
                else:
                    candidateTuple.append(None)
            tupleList.append(tuple(candidateTuple))
            i += 1

        return tupleList
        # e.g., parameter 1= , c1= , t1=

    def correlateTuplesInTemplateArguments(self,root1,root2,templateArgumentDictionary):
        if type(root1) is not str or type(root2) is not str:
            raise Exception("root passed to collectAllTemplateArgumentValuesDedupe must be a string!")

        if root1 not in templateArgumentDictionary or root2 not in templateArgumentDictionary:
            return None

        returnTupleList = []

        firstTuple = (templateArgumentDictionary[root1] if root1 in templateArgumentDictionary else None,
                      templateArgumentDictionary[root2] if root2 in templateArgumentDictionary else None)

        returnTupleList.append(firstTuple)

        i = 2
        while root1 + str(i) in templateArgumentDictionary or root2 + str(i) in templateArgumentDictionary:
            root1Argument = root1 + str(i)
            root2Argument = root2 + str(i)
            nextReturnTuple = (templateArgumentDictionary[root1Argument] if root1Argument in templateArgumentDictionary
                               else None,
                               templateArgumentDictionary[root2Argument if root2Argument in templateArgumentDictionary
                               else None])
            returnTupleList.append(nextReturnTuple)
            i += 1

        return returnTupleList

    def _findCharAnalysisDictForChar(self, character):
        if character not in self.characterAnalysisDict:
            self.characterAnalysisDict[character] = {}

        return self.characterAnalysisDict[character]

    # need to test, especially handling of page titles that are not chars, like "東/derived terms"
    # are the internal dicts correct?

    def _makeSureListInDict(self, dictionary, key):
        if type(dictionary) is not dict:
            raise Exception("makeSureListInDict requires type dict and was not passed such.")

        if key in dictionary:
            if type(dictionary[key]) is not list:
                raise Exception("makeSureListInDict expects a list to be at the passed key value.")
            return dictionary[key]

        # key is not in dictionary
        dictonary[key] = []
        return dictionary[key]

    def _makeSureSetInDict(self, dictionary, key):
        if type(dictionary) is not dict:
            raise Exception("makeSureSetInDict requires type dict and was not passed such.")

        if key in dictionary:
            if type(dictionary[key]) is not set:
                raise Exception("makeSureSetInDict expects a set to be at the passed key value, if the key exists.")
            return dictionary[key]

        # key is not in dictionary
        dictionary[key] = set()
        return dictionary[key]

    def _numberOfOverflowTemplates(self, templateValuesForPage, templateName):
        if __overflow__ not in templateValuesForPage:
            return None
        elif templateName not in templateValuesForPage[__overflow__]:
            return 0
        else:
            return len(templateValuesForPage[__overflow__][templateName])

    def _grabOverflowTemplateDict(self, templateValuesForPage, templateName, overflowNumber):
        return templateValuesForPage[__overflow__][templateName][overflowNumber]

    def _grabPrincipalTemplateDict(self, templateValuesForPage, templateName):
        templateName = self._processedTemplateMainSpelling(templateName)
        if templateName not in templateValuesForPage:
            return None

        return templateValuesForPage[templateName]
        # allow possible handling of variant forms of the same template in the future. But, for now...

    def _overflowHandle(self, handlerToCall, templateToSeek, pageTitle, templateValuesForPage):
        overflowCount = self._numberOfOverflowTemplates(templateValuesForPage, templateToSeek) # again, must account for variant template names
        # print("overflowCount = ",overflowCount)
        if overflowCount is not None:
            for i in range(0,overflowCount):
                # print("calling grabOverflowTemplateDict on i = ",i," for template ",templateToSeek)
                grabbedOverflowDict = self._grabOverflowTemplateDict(templateValuesForPage,templateToSeek,i)
                handlerToCall(pageTitle, templateValuesForPage, overflowDict=grabbedOverflowDict)

    def _testForTemplate(self, templateValuesForPage, templateName):
        # this function allows us to program in alternate spellings for the template at a later date without hard coding it
        if templateName not in templateValuesForPage:
            return False
        else:
            return True

    def __init__(self):
        pass


