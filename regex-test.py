import re

def getSetup(input):
    setupregex = r"%regex:(.+),(.+)\n"
    return re.findall(setupregex, input)
    

with open("test.md", "r") as file:
    content = file.read()
    print(content)

    setupstr = "%regex:<!--(.+)-->,\\\marginpar{\g<1>}\n%regex:<!--(asd)-->,gff\n"
    for setup in getSetup(setupstr):
        print(setup[1])
        content = re.sub(setup[0], setup[1], content)
    with open("test2.md", "w") as out:
        out.write(content)


