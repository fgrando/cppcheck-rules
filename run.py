import subprocess
import os
import re
import shutil
import xml.etree.ElementTree as ET

# loaded rules list:
rules= []

from Rule1 import *
rules.append(Rule1())

#import Rule2
#rules.append(Rule2())

#import Rule3
#rules.append(Rule3())


# configurations
sources='C:/Users/fgrando/Downloads/cppcheck-rules/'
workspace='C:/Users/fgrando/Downloads/cppcheck-rules/ws'
cppcheckDir='C:/Users/fgrando/Downloads/cppcheck-2.3/cppcheck-2.3/bin/debug'
cppcheckBin='cppcheck.exe'


def sourceFilesList(path, regex):
    out = []
    for f in os.listdir(path):
        if re.match(regex, f):
            out.append(os.path.join(path, f))
    return out


def runCppCheck(src, dst):
    cppcheck = os.path.join(cppcheckDir, cppcheckBin)
    cmd = cppcheck + " -q --language=c++ --dump " + src
    # cppcheck generates a file with the .dump extension in the source folder.
    # move this file to the destination
    ret = subprocess.run(cmd.split(), stdout=subprocess.PIPE, cwd=cppcheckDir)
    output = ret.stdout.decode('utf-8')

    if output != "":
        print(f"Possible failure converting {src}: {output}")
        exit(-1)

    shutil.move(src+'.dump', dst)


print("Enabled rules:")
for rule in rules:
    rule.show()
print("\n\n\n")

for src in sourceFilesList(sources, ".*\.h$"):
    name = os.path.basename(src)
    print(f"processing {name} ...")
    dst = os.path.join(workspace, name+'.xml')
    runCppCheck(src, dst)

    # load the xml
    tree = ET.parse(dst)
    root = tree.getroot()

    for rule in rules:
        rule.check(root)


