from Rule import Rule
import re

class Rule1(Rule):
    def __init__(self):
        Rule.__init__(self, 1, "All Class member variables must start with underscore '_'")

    def check(self, xml):
        dumps = xml.findall("./dump")

        for d in dumps:
            for scope in d.findall("./scopes/scope"):
                if scope.attrib.get('type') == 'Class':
                    self.log.debug(scope.attrib)

                    for var in scope.findall("./varlist/var"):
                        id = var.attrib.get('id')
                        varData = self.getVar(id, xml)
                        tokData = self.getToken(varData.attrib.get('nameToken'), xml)

                        name = tokData.attrib.get('str')
                        file = tokData.attrib.get('file')
                        line = tokData.attrib.get('linenr')
                        if not re.match('^_\w+', name):
                            self.raiseError(file, line, name)

                        #print(varData.attrib)
                        #print(tokData.attrib)