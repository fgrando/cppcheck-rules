import logging

class Rule:
    def __init__(self, num, txt):
        self.msg = txt
        self.number = num
        self.log = logging.getLogger('output.txt')
        self.log.setLevel(logging.DEBUG)

    def check(self, xml):
        self.log.error("implemented by derived classes....")

    def raiseError(self, file, line, offender):
        self.log.error(f"[R{self.number}] {file}:{line}: {offender}\t|{self.msg}")

    def show(self):
        self.log.error(f"Rule {self.number}: {self.msg}\n\tSome explanation about this rule.")

    def getVar(self, id, xml):
        for v in xml.findall("./dump/variables/var"):
            if id == v.attrib.get('id'):
                return v

        self.log.error(f"Possible bug: var {id} not found!")
        return None

    def getToken(self, id, xml):
        for t in xml.findall("./dump/tokenlist/token"):
            if id == t.attrib.get('id'):
                return t
        self.log.error(f"Possible bug: var {id} not found!")
        return None