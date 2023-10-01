from tkinter.filedialog import askopenfilename
import os
from pathlib import Path
import re


# Implement template config files and the possibility of merging the note export script into this one though said config files
# Ideas for config options:
# Use bibber(or not)
# Template name
# Template path
# Preprocessing steps/commands
# post processing steps/commands

def selectTemplate(templateDir="C:\\Users\\sfgar\\programing\\markdown-publisher\\templates"):
    templates = [x for x in Path(templateDir).glob("template_*.tex")]

    for i, template in enumerate(templates):
        print(str(i+1)+": "+template.stem.replace("template_",""))

    return templates[int(input("Select template: "))-1]

def getdocxTemplate(templatePath):
    path = Path(str(templatePath).replace(".tex", ".docx"))

    if path.exists():
        return path
    else:
        return None


def genPDF(mdfile, template):
    parentDir = mdfile.parent

    outputname = parentDir / mdfile.stem
    auxfolder = parentDir / "latex-aux"

    os.system('pandoc --from markdown+pipe_tables+footnotes+inline_notes -s "'+str(mdfile)+'" -o "'+str(outputname)+'.tex" --template "'+str(template)+'" --biblatex')
    os.system('latexmk -xelatex -pdf -output-directory="'+str(parentDir)+'" -auxdir="'+str(auxfolder)+'" "'+str(outputname)+'.tex"')

## Add this so I can use it to export revealjs slides with citations
def expandCitationsMarkdown(mdfile, outputfile):
    os.system("pandoc -t markdown_strict '"+str(mdfile)+"' -o '"+str(outputfile)+"' --standalone --citeproc")

def genDocx(mdFile, docxTemplate):
    parentDir = mdFile.parent

    outputname = parentDir / mdFile.stem

    if docxTemplate:
        refdoc = "--reference-doc="+str(docxTemplate)
    else:
        refdoc = ""

    os.system('pandoc --citeproc "'+str(outputname)+'.tex" '+refdoc+' -o "'+str(outputname)+'.docx"')

def processMd(mdfile, template):
    def getSetup(input):
        setupregex = r"%regex:(.+),(.+)\n"
        return re.findall(setupregex, input)
    
    outfilename = "test2.md"
    file = open(mdfile, "r")
    templatefile = open(template, "r")
    outputfile = open(outfilename, "w")

    content = file.read()

    for setup in getSetup(templatefile.read()):
        content = re.sub(setup[0], setup[1], content)

    outputfile.write(content)

    file.close()
    templatefile.close()
    outputfile.close()

    return Path(outfilename)





mdfile = Path(askopenfilename())
print("\n\n")
print("Processing: "+str(mdfile))
print("====================\n\n")

template = selectTemplate()

docxTemplate = getdocxTemplate(template)

print("\n\n")
if docxTemplate:
    print("Found docx template: "+str(docxTemplate))
else:
    print("Couldn't find docx template... using default")
print("====================\n\n")


while True:
    output = input("Press any button to regenerate PDF (or w+enter to generate word doc+pdf)")
    if(output == "w"):
        genPDF(mdfile, template)
        genDocx(mdfile, docxTemplate) # This uses mdfile since it should include regex changes???
    elif(output == "a"):
        print("")
    else:
        genPDF(mdfile, template)
    