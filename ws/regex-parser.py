import re


class Edge:
    def __init__(self, start, end, name):
        self.src = start
        self.dst = end
        self.name = name

    def __str__(self):
        return f"{self.src} --- {self.name} --> {self.dst}"



class CppCheckXmlParser:
    def __init__(self, xml_path):
        self.complex_types_names = ['record', 'container'] # type that cppcheck gives to complex types and structs
        self.dom = minidom.parse(xml_path)
        self.structs = self.get_raw_structs()
        self.variables = self.get_raw_variables()
        self.token_vars = self.get_token_variables()

    def get_token_variables(self):
        """ Returns all attributes of the tokens """
        items = []
        tokens = self.dom.getElementsByTagName('token')
        for element in tokens:
            item = {}
            try:
                # test to see if the 'variable' attribute is there
                v = element.attributes['variable']
                for i in element.attributes.items():
                    item[i[0]] = i[1]
                items.append(item)
            except:
                pass
        return items

    def get_raw_structs(self):
        """ Returns all attributes of the structs """
        elements = self.dom.getElementsByTagName('scope')
        items = []
        for element in elements:
            if 'Struct' == element.attributes['type'].value:
                item = {}
                for i in element.attributes.items():
                    item[i[0]] = i[1]
                items.append(item)
        return items

    def get_raw_variables(self):
        """ Returns all attributes of the variables section """
        items = []
        variables_root = self.dom.getElementsByTagName('variables')
        for variable in variables_root:
            children = variable.childNodes
            for v in children:
                if v.nodeType ==  minidom.Node.ELEMENT_NODE:
                    item = {}
                    for i in v.attributes.items():
                        item[i[0]] = i[1]
                    items.append(item)
        return items


    def get_edges(self):
        edges = []
        for v in self.variables:
            nameToken = v['nameToken']
            token = None

            # get var data
            for x in self.token_vars:
                if x['id'] == nameToken:
                    token = x
                    break

            name = token['str']
            
            # get struct src
            src = None
            for x in self.structs:
                if x['id'] == token['scope']:
                    src = x['className']
                    break

            # get dest
            dst = token['valueType-type']
            if dst == 'record':
                # resolve to the struct name
                for x in self.structs:
                    if x['id'] == token['valueType-typeScope']:
                        dst = x['className']
                        break

            # create the special type for the pointer
            if v['isPointer'] == 'true': # int(token['valueType-pointer']) != 0:
                dst = f"{dst}*"

            e = Edge(src, dst, name)
            edges.append(e)
        return edges


def recursive_print(node, edges, nodes, basic_nodes, prefix=''):
    if node in basic_nodes:
        print(f'# {prefix}')
    else:
        others = []
        mentioned = []
        for e in edges:
            if e.src == node:
                mentioned.append(e)
            else:
                others.append(e)
        
        for e in mentioned:
            new_prefix = f"{prefix}.{e.name}"
            if e.dst in basic_nodes:
                print(f"\t{e.dst} {new_prefix}")
            else:
                # go again to process all struct fields:
                recursive_print(e.dst, others, nodes, basic_nodes, new_prefix)














def removeComments(text):
    """ remove c-style comments.
        text: blob of text with comments (can include newlines)
        returns: text with comments removed
    """
    pattern = r"""
                            ##  --------- COMMENT ---------
           //.*?$           ##  Start of // .... comment
         |                  ##
           /\*              ##  Start of /* ... */ comment
           [^*]*\*+         ##  Non-* followed by 1-or-more *'s
           (                ##
             [^/*][^*]*\*+  ##
           )*               ##  0-or-more things which don't start with /
                            ##    but do end with '*'
           /                ##  End of /* ... */ comment
         |                  ##  -OR-  various things which aren't comments:
           (                ##
                            ##  ------ " ... " STRING ------
             "              ##  Start of " ... " string
             (              ##
               \\.          ##  Escaped char
             |              ##  -OR-
               [^"\\]       ##  Non "\ characters
             )*             ##
             "              ##  End of " ... " string
           |                ##  -OR-
                            ##
                            ##  ------ ' ... ' STRING ------
             '              ##  Start of ' ... ' string
             (              ##
               \\.          ##  Escaped char
             |              ##  -OR-
               [^'\\]       ##  Non '\ characters
             )*             ##
             '              ##  End of ' ... ' string
           |                ##  -OR-
                            ##
                            ##  ------ ANYTHING ELSE -------
             .              ##  Anything other char
             [^/"'\\]*      ##  Chars which doesn't start a comment, string
           )                ##    or escape
    """
    regex = re.compile(pattern, re.VERBOSE|re.MULTILINE|re.DOTALL)
    noncomments = [m.group(2) for m in regex.finditer(text) if m.group(2)]

    return "".join(noncomments)

def commentRemover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)


class RegexParser:
    def __init__(self, header):
        txt = open(header).read()
        self.txt = commentRemover(txt)

    def get_edges(self):
        edges = []
        # starting with typedef
        structs_1 = re.findall('(?<=typedef\sstruct).*?}\s[\w]+;', self.txt, re.DOTALL)

        for s in structs_1:
            inside_brackets = re.findall('\{.*\}', s, re.DOTALL)
            if len(inside_brackets) > 0:
                content = inside_brackets[0]

                struct_name = s.replace(content, '')
                struct_name = struct_name.replace(';','')
                src = struct_name.strip()
                
                content = content.replace('{','').strip()
                content = content.replace('}','').strip()
                content = content.split(';')
                for c in content:
                    if len(c) > 0:
                        var = c.split()
                        parts = len(var)
                        name = var[-1]
                        dst = ' '.join(var[:parts-1])
                        #print(f"{src} --> {name} --> {dst}")
                        e = Edge(src, dst, name)
                        edges.append(e)
        return edges


class Graph:
    def __init__(self):
        self.nodes_basic = []
        self.nodes = []
        self.edges = []

    def load(self, cppcheck_xml_path):
        basic = set()
        structs = set()
        parser = RegexParser(cppcheck_xml_path)
        self.edges = parser.get_edges()

        # find the nodes that have no children (basic types)
        for e in self.edges:
            structs.add(e.src) # sources are never basic types
            node = e.dst

            # if this node is alredy a basic type, no need to test again
            if node in basic:
                continue

            # test if the node is a basic type
            isBasicType = True
            for n in self.edges:
                if node == n.src:
                    isBasicType = False
                    break

            if isBasicType:
                basic.add(node)
            else:
                structs.add(node)

        self.nodes_basic = list(basic)
        self.nodes = list(structs)

        
        

    def print_listing(self):
        for n in self.nodes:
            print(f"{n}:")
            recursive_print(n, self.edges, self.nodes, self.nodes_basic, prefix=f'___{n}')
        print('===========================')


g = Graph()
g.load('../icd.h')
g.print_listing()

