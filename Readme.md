# Origins

Origins is a python3 script that processes Wiktionary dictionary pages for Chinese characters in order to show the relationships among them.

## Overview
### Quick Start
1) Take note of the included `pageDict.json` or generate a fresh one by running `parseWiki.py` on a Wiktionary dump
   file as described below.
2) `sudo pip3 install wikitextparser`
2) `./pullRelationships.py pageDict.json`

A `pageDict.json` is included here, but if you want to generate a fresh one, run `./parseWiki.py` after step 1)
on a Wiktionary articles dump  file as described below.

### What This Is And Why I Wrote It
Chinese characters are a written "code" with graphical clues as to their meaning. I am a language hobbyist and started
learning Mandarin on Duolingo, but found it difficult to read because of the sheer number of written symbols.

So, I decided to work on this project, with the ultimate aim of deriving my own study aid from Wiktionary.

### Current State Of The Program
At present, the program processes a Wiktionary dump file into a list of relationships asserted by 5 key Wiktionary templates.
You can see sample output connecting two characters below. The first is the traditional character for "love"; the 
second is the character for "heart." The "love" character includes a drawing of a heart. If you increase the font size,
you can see that this is true. By learning the character for "heart", you have a better chance of remembering or guessing
the meaning of the character for the word "love".

> PAGE:  11 		 愛
{'compoundType': {'phono-semantic compound'},
'hasComponent': {'旡', '心'},
'hasPhoneticComponent': {'旡'},
'hasSemanticComponent': {'心'},
'mainSimplified': {'爱'},
'simplifiedBy': {'爱'},
'type': {'traditional character'}}

> PAGE:  90 		 心
{'isComponentOf': {'愛'},
'isSemanticComponentOf': {'愛'},
'translation': {'heart'},
'type': {'same simplified and traditional'}}

### Future Directions
My ultimate goal is to eventually have this program analyze the resulting relationships to produce useful,
second-level data. For example, there is a one-to-many relationship between common character components and characters
where they are used.

I am also interested in displaying the data in more interesting ways. Each character has a dictionary meaning and pronunciation,
for example, which is not listed here.

There are more relationships among Chinese characters than are documented in Wiktionary, so this program can be used
to show gaps in Wiktionary entries.

### Caveats

There are better, more scholarly study aids available for Chinese characters. Moreover, there are many more efficient
ways to store data about Chinese characters, and more efficient ways to process Wiktionary algorithmically.

I do not pretend to be the best source for either. However, I had tremendous fun producing this program and find it
to be easy for me to work with.

The accuracy of any underlying data is limited by the accuracy of publicly accessible Wiktionary pages.

## Documentation
### Command Line
`./parseWiki.py [-h] [--output-file <<OUTPUT_FILE>>] <<wiki_file_to_parse>>`

Call `parseWiki` on a Wiktionary dump file, in either plain `xml`, `xml.gz`, or `xml.bz2` format. Wiktionary dump files are available from
https://dumps.wikimedia.org/. The file of interest is an "articles" dump of English-language Wiktionary, typically named 
`enwiktionary-<<date>>-pages-articles`. Optionally, the name of `<<OUTPUT_FILE>>` can be specified; it is `pageDict.json` by default.

The resultant .json file is a simple JSON object, equivalent and interchangeable with a Python dictionary.
The keys of the object are the names of pages in Wiktionary, and the values of the object are Wikitext from those pages.
Data is filtered and only stored if it meets the following criteria:
1) The page title is either a single character in the CJK set, or else a single character plus the text "/derived terms".
2) The page contains Wikitext in a section labeled "Chinese". Only the Wikitext from that section will be stored. If no such section exists,
the page will not be stored in the object.
   
parseWiki uses the standard filestream object interface to the gzip and bz2 libraries, for ease of maintenance.
As a result, processing time may be significant, on the order of 15 minutes. However, the resulting file is
much smaller and can be processed quickly.

`./pullRelationships.py [-h] [--output-file OUTPUT_FILE] pageDict`

`pullRelationships` analyzes a page dictionary file produced by `parseWiki`, pulling selected information about Chinese
characters from the following Wiktionary templates. Template syntax is (partially) documented in Wiktionary pages such as
https://en.wiktionary.org/wiki/Template:zh-forms, with a URL based on the template name. The resulting relationships are
output to standard out from an internal Python "set" format, and also converted to lists before being output to
`OUTPUT_FILE` (by default, `relationships.json`)

1) `zh-forms`: Information about traditional Chinese characters and their simplified equivalents.
2) `zh-see`: More nuanced information about various variant forms of characters, including simplified variants
   and traditional variants.
3) `Han simp`: Information on how Chinese characters were simplified and what components were simplified to
   what simplified forms.
4) `Han compound`: Information about how several different Chinese characters were combined into a single character,
   along with the liu shu category for each: whether a character is an ideogram representing a single idea, a
   compound of several ideas, or a phono-semantic compound of both a "sound" clue and a "sense" clue. Because
   language sounds change over time, but semantic relationships are more stable, I made a choice to focus on pulling out
   the "sense" information.
5) `liushu`: Contains the liu shu category of a character.

### Dependencies
Origins is written in Python 3.

Origins depends on `wikitextparser` 0.47 or higher, a regular expression-based parser of Wikimedia templates. 

## Legal
### License and Disclaimer of Warranty
> This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. 
> 
> This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details. 
>
>You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
### Processed Wiktionary Files
To the extent that this project includes processed Wiktionary files (e.g., pageDict.json), I claim no authorship to
these files. The copyright and license are as described on Wiktionary by the original authors.

Per https://en.wiktionary.org/wiki/Wiktionary:Copyrights,
The original texts of Wiktionary entries are dual-licensed to the public under both the Creative Commons Attribution-ShareAlike 3.0
Unported License (CC-BY-SA) and the GNU Free Documentation License (GFDL). The full text of both licenses can be found at
Wiktionary:Text of Creative Commons Attribution-ShareAlike 3.0 Unported License, as well as Wiktionary:Text of the GNU Free Documentation License.
Permission is granted to copy, distribute and/or modify the text of all Wiktionary entries under the terms of the Creative Commons
Attribution-ShareAlike 3.0 Unported License, and the GNU Free Documentation License, Version 1.1 or any later version published by
the Free Software Foundation; with no Invariant Sections, with no Front-Cover Texts, and with no Back-Cover Texts.
