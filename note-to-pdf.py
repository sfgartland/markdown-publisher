import os
from pathlib import Path
import re


notepath = Path("input.md")

def hardEmbed(content):
    localEmbeds = re.findall("!\[\[#(.+)\]\]", content)
    for localEmbed in localEmbeds:
        quoteregex = ">.+\n>\n>(.+)(\\"+localEmbed+")"
        #print(quoteregex)
        quote = re.search(quoteregex, content)
        #print(quote.group(1))
        content = content.replace("![[#"+localEmbed+"]]", quote.group(1))
    return content

def cleanUpZoteroQuotes(content):
    re_linkAndDate = "(\(zotero:\/\/open-pdf.+\)\s\[\[\d{4}-\d{2}-\d{2}#\d{2}:\d{2}\s\w{2}\]\]\s)"
    content = re.sub(re_linkAndDate, "", content)
    return content

def pageRefToPandocRef(content, citekey):
    re_pageRef = "(\(p{1,2}\. (\d+)(-|,)?(\d+)?\))"
    pageRefs = re.findall(re_pageRef, content)
    pandocPageRef = None
    for pageRef in pageRefs:
        # This block allows taking in e.g. "(p. 10-3)" in the form of an array and expands it to "pp. 10-13"
        if pageRef[3] != "":
            fromPage = int(pageRef[1])
            toPage = int(pageRef[3])
            listOrRange = pageRef[2]
            if listOrRange == "-" and fromPage > toPage:
                missingDigits = len(str(fromPage))-len(str(toPage))
                toPage = int(str(fromPage)[:missingDigits]+str(toPage))
            pandocPageRef = "[@"+citekey+", p. "+str(fromPage)+listOrRange+str(toPage)+"]"
        else:
            pandocPageRef = "[@"+citekey+", p. "+pageRef[1]+"]"
        content = content.replace(pageRef[0], pandocPageRef)
    return content



def extractNoteSection(content):
    return content.split("%% begin notes %%")[1].split("%% end notes %%")[0]

with open(notepath, "r") as note:
    content = note.read()
    content = hardEmbed(content)
    content = extractNoteSection(content)
    content = cleanUpZoteroQuotes(content)
    content = pageRefToPandocRef(content, notepath.stem)

    with open("output.md", "w") as newNote:
        newNote.write(content)