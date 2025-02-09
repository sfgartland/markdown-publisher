from tkinter.filedialog import askopenfilename
import os
from pathlib import Path

from typing import Optional, List

from typing_extensions import Annotated

import typer

import inquirer
import shutil


# Implement template config files and the possibility of merging the note export script into this one though said config files
# Ideas for config options:
# Use bibber(or not)
# Template name
# Template path
# Preprocessing steps/commands
# post processing steps/commands


def getTemplates(
    templateDir=Path("C:\\Users\\sfgar\\programing\\markdown-publisher\\templates"),
    localDir: Path = None,
) -> List[Path]:
    templates = [Path(x) for x in templateDir.glob("template_*.tex")]
    local_templates = []
    if localDir:
        local_templates = [x for x in localDir.glob("template_*.tex")]

    return (templates, local_templates)


def selectTemplate(localDir: Path):
    templates, local_templates = getTemplates(localDir=localDir)
    templateMap = {}
    for i, template in enumerate(local_templates):
        templateMap[f"(local) {template.stem}"] = template
    for i, template in enumerate(templates):
        templateMap[template.stem] = template

    # templateMap["(Select using file dialog)"] = None

    selection = inquirer.list_input(
        message="Select a template",
        choices=templateMap.keys(),
    )

    # if selection == "(Select using file dialog)":
    #     return selectFile([FileTypes.tex])
    # else:
    return templateMap[selection]


def getdocxTemplate(templatePath):
    path = Path(str(templatePath).replace(".tex", ".docx"))

    if path.exists():
        return path
    else:
        return None


def genPDF(mdfile, template):
    parentDir = mdfile.parent

    outputname = parentDir / mdfile.stem
    workdir = parentDir / "pandoc-workdir"
    workdir.mkdir(exist_ok=True)
    auxfolder = workdir / "latex-aux"

    os.system(
        f'pandoc --from markdown+pipe_tables+footnotes+inline_notes -s "{mdfile}"  -o "{outputname}.tex" --template "{template}" --biblatex'
    )
    os.system(
        f'latexmk -xelatex -output-directory="{workdir}" -auxdir="{auxfolder}" "{outputname}.tex"'
    )
    shutil.copy(workdir / f"{outputname}.pdf", parentDir / f"{outputname}.pdf")


def genDocx(mdFile, docxTemplate):
    parentDir = mdFile.parent

    temp_outputname = parentDir / "pandoc-workdir" / mdFile.stem
    perm_outname = parentDir / mdFile.stem

    if docxTemplate:
        refdoc = "--reference-doc=" + str(docxTemplate)
    else:
        refdoc = ""

    os.system(
        'pandoc --citeproc "'
        + str(temp_outputname)
        + '.tex" '
        + refdoc
        + ' -o "'
        + str(temp_outputname)
        + '.docx"'
    )
    shutil.copy(temp_outputname.with_suffix(".docx"), perm_outname.with_suffix(".docx"))


class FileTypes:
    md = ("Markdown files", "*.md")
    tex = ("LaTeX files", "*.tex")
    docx = ("Word files", "*.docx")


def selectFile(filetypes: List[FileTypes] = []) -> Path:
    selectedFile = Path(
        askopenfilename(
            initialdir=os.getcwd(), filetypes=[*filetypes, ("All files", "*.*")]
        )
    )
    return Path(selectedFile)


def main(
    file: Annotated[
        Optional[Path],
        typer.Argument(
            help="Markdown file to process",
        ),
    ] = None,
    templatefile: Annotated[
        Optional[Path],
        typer.Argument(help="Template file"),
    ] = None,
    docxtemplate: Annotated[
        Optional[Path], typer.Argument(help="Docx template file")
    ] = None,
):
    if file is None:
        file = selectFile([FileTypes.md])

    if templatefile is None:
        templatefile = selectTemplate(file.parent)

    if docxtemplate is None:
        docxtemplate = getdocxTemplate(templatefile)
        if docxtemplate is None:
            print("No docx template found... Using default")


    while True:
        output = input(
            "Press any button to regenerate PDF (or w+enter to generate word doc+pdf)"
        )
        if output == "w":
            genPDF(file, templatefile)
            genDocx(
                file, docxtemplate
            )
        else:
            genPDF(file, templatefile)


def cli():
    typer.run(main)


if __name__ == "__main__":
    cli()
