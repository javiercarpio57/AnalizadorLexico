import re

class AnalisisLexico():
    def __init__(self, config):
        print(' -- INICIALIZANDO -- ')
        self.compiler = None
        self.characters = {}
        self.keywords = {}
        self.tokens = {}
        self.productions = []

        self.parse(config)

    def precedence(self, op):
        if op == '+' or op == '-':
            return 1
        return 0
    
    def applyOp(self, a, b, op):
        if op == '+': return self.union(a, b)
        if op == '-': return self.difference(a, b)

    def union(self, a, b):
        return a + '|' + b
    
    def difference(self, a, b):
        return '|'.join(list(set(a.split('|')) - set(b.split('|'))))

    def evaluate(self, tokens):
        values = []
        ops = []
        i = 0
        
        while i < len(tokens):
            if tokens[i] == '(':
                ops.append(tokens[i])
            
            elif tokens[i] not in '()+-':
                val = ''
                while i < len(tokens) and tokens[i] not in '()+-':
                    val += tokens[i]
                    i += 1
                
                values.append(val)
                i-=1

            elif tokens[i] == ')':
            
                while len(ops) != 0 and ops[-1] != '(':
                    val2 = values.pop()
                    val1 = values.pop()
                    op = ops.pop()
                    
                    values.append(self.applyOp(val1, val2, op))
                ops.pop()
            
            else:
                while len(ops) != 0 and self.precedence(ops[-1]) >= self.precedence(tokens[i]):
                    val2 = values.pop()
                    val1 = values.pop()
                    op = ops.pop()
                    
                    values.append(self.applyOp(val1, val2, op))
                ops.append(tokens[i])
            
            i += 1
        while len(ops) != 0:
            val2 = values.pop()
            val1 = values.pop()
            op = ops.pop()
                    
            values.append(self.applyOp(val1, val2, op))
        return values[-1]

    def parse(self, config):
        compiler = None
        characters = []
        keywords = []
        tokens = []
        productions = []
        
        isCompiler = False
        isCharacters = False
        isKeywords = False
        isTokens = False
        isProductions = False

        temp = ''
        for c in config_file:
            words = c.split()

            if words[0].lower() == 'compiler':
                isCompiler = True
                isCharacters = False
                isKeywords = False
                isTokens = False
                isProductions = False
            elif words[0].lower() == 'characters':
                isCompiler = False
                isCharacters = True
                isKeywords = False
                isTokens = False
                isProductions = False
            elif words[0].lower() == 'keywords':
                isCompiler = False
                isCharacters = False
                isKeywords = True
                isTokens = False
                isProductions = False
            elif words[0].lower() == 'tokens':
                isCompiler = False
                isCharacters = False
                isKeywords = False
                isTokens = True
                isProductions = False
            elif words[0].lower() == 'productions':
                isCompiler = False
                isCharacters = False
                isKeywords = False
                isTokens = False
                isProductions = True
            elif words[0].lower() == 'end':
                break

            if isCompiler:
                compiler = words[1]
                isCompiler = False
            elif isCharacters:
                characters.append(c)
            elif isKeywords:
                keywords.append(c)
            elif isTokens:
                temp += c
                if c[-1] == '.' or temp == 'TOKENS':
                    tokens.append(temp)
                    temp = ''
            elif isProductions:
                temp += c
                if c[-1] == '.' or temp == 'PRODUCTIONS':
                    productions.append(temp)
                    temp = ''

        if len(characters) > 0:
            characters.pop(0)
        
        if len(keywords) > 0:
            keywords.pop(0)

        if len(tokens) > 0:
            tokens.pop(0)

        if len(productions) > 0:
            productions.pop(0)

        print('---------------------- CHARACTERS ------------------------------------------------------')
        for p in characters:
            print(p)
        print('---------------------- TOKENS---- ------------------------------------------------------')
        for p in tokens:
            print(p)
        # print('----------------------------------------------------------------------------')
        # for p in productions:
        #     print(p)
        
        self.compiler = compiler
        self.buildCharacters(characters)
        self.buildKeywords(keywords)
        self.buildTokens(tokens)
        self.productions = productions
        
    def buildCharacters(self, characters):
        any_array = '|'.join(chr(i) for i in range(48, 123))
        # characters.insert(0, any_array)

        pattern = '(CHR\([0-9]*\))'
        for i in range(len(characters)):
            matches = re.findall(pattern, characters[i])
            newCharacter = characters[i]
            for m in matches:
                newCharacter = newCharacter.replace(m, eval(m.lower()))

            characters[i] = newCharacter

        self.characters['ANY'] = any_array
        # print(self.characters)

        for char in characters:
            char = char.replace(' ', '')
            character = char.split('=')
            
            plus = []
            for ch_plus in character[1].split('+'):
                minus = []
                for ch_minus in ch_plus.split('-'):
                    text = ''
                    ch_minus = ch_minus.replace('.', '')
                    if ch_minus[0] == '"' and ch_minus[-1] == '"':
                        ch_minus = ch_minus.replace('"', '')
                        for i in range(len(ch_minus)):
                            if i < len(ch_minus) - 1:
                                text += ch_minus[i] + '|'
                            else:
                                text += ch_minus[i]
                        text = '(' + text + ')'
                    elif ch_minus in self.characters.keys():
                        text = self.characters[ch_minus]
                    else:
                        text += ch_minus
                    minus.append(text)
                plus.append('-'.join(minus))

            self.characters[character[0]] = '+'.join(plus)

        for key, value in self.characters.items():
            result = self.evaluate(value)
            self.characters[key] = '(' + result + ')'
        print(self.characters)


    def buildKeywords(self, keywords):
        for kw in keywords:
            kw = kw.replace(' ', '')
            keyword, word = kw.split('=')
            word = word[:-1]
            
            self.keywords[word.replace('"', '')] = keyword.replace('"', '')

    def buildTokens(self, tokens):
        listCharacters = list(self.characters.keys())
        listCharacters.sort(key = len)
        listCharacters.reverse()

        clean_tokens = []
        for token in tokens:
            newToken = token
            for character in listCharacters:
                if character in newToken:
                    newToken = newToken.replace(character, self.characters[character])
            clean_tokens.append(newToken)

        for token in clean_tokens:
            token = token.replace(' ', '')
            tok = token.split('=')
            self.tokens[tok[0]] = {}
            self.tokens[tok[0]]['expresion'] = tok[1][:-1]
            self.tokens[tok[0]]['except'] = {}


        for key, value in self.tokens.items():
            if 'EXCEPT' in value['expresion']:
                exceptions = value['expresion'].split('EXCEPT')
                self.tokens[key]['expresion'] = exceptions[0]

                if exceptions[1].replace('.', '') == 'KEYWORDS':
                    self.tokens[key]['except'] = self.keywords

            if '{' in value['expresion'] and '}' in value['expresion']:
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace('{', '(')
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace('}', ')*')

            if '[' in value['expresion'] and ']' in value['expresion']:
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace('[', '(')
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace(']', ')?')

            if '"' in value['expresion']:
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace('"', '')


config_file = []

archivo = input('Ingrese el nombre del archivo ATG: ')

with open(archivo, 'r') as reader:
    for line in reader:
        if line != '\n':
            config_file.append(line.strip())


analisislexico = AnalisisLexico(config_file)

print()

tokens_program = ''
exception_program = ''

for key, value in analisislexico.tokens.items():
    tokens_program += '"' + key + '": ' + repr(value['expresion']) + ',\n'
    exception_program += '"' + key + '": ' + str(value['except']) + ',\n'



programa_completo = '''

import functools
import utilities
from time import perf_counter
epsilon = 'ε'

class DFA_Node():
    def __init__(self, name, nodos, isDirect = False):
        self.name = name
        self.id = None
        self.conjunto_nodos = nodos
        self.transitions = []
        self.isMarked = False
        self.isFinal = False

        if not isDirect:
            self.CreateID(nodos)
        else:
            self.CreateID2(nodos)

    # Metodo para crear un ID unico para el nodo.
    def CreateID(self, nodos):
        a = [n.id for n in nodos]
        a.sort()
        a = [str(i) for i in a]
        self.id = ', '.join(a)

    # Metodo para crear ID unico para hoja de arbol sintactico.
    def CreateID2(self, nodos):
        a = [n for n in nodos]
        a.sort()
        a = [str(i) for i in a]
        self.id = ', '.join(a)

    # Metodo para marcar un estado que ya ha sido visitado.
    def Mark(self):
        self.isMarked = True

    # Metodo para definir un estado como de aceptacion.
    def isAcceptingState(self):
        self.isFinal = True

class SyntaxTree():
    def __init__(self, regular_expression, all_symbols, tokens):
        self.count = 0
        self.rounds = 1
        self.estados = []

        self.simbolos_aceptables = all_symbols
        self.simbolos = []
        self.transiciones = []
        self.estados_aceptacion = []
        self.estado_inicial = None
        
        self.nodos = []
        self.root = None
        self.id = 0
        self.primera_vez = True
        self.estado_final = []

        self.tokens = {}
        self.nombres_estados = {}

        self.follow_pos = {}
        regular_expression = self.CleanExpression(regular_expression)
        regular_expression = self.CreateConcat(regular_expression)
        # print('EXPRESION FIXED:', regular_expression)

        self.evaluate(regular_expression)

        cont = 0
        for n in self.nodos:
            if n.name == '#':
                self.estado_final.append(n.position)
                self.tokens[n.position] = tokens[cont]
                cont += 1

        self.calculate_followpow()
        self.create_dfa()

    def intersection(self, lst1, lst2):
        lst3 = [value for value in lst1 if value in lst2]
        return lst3

    # Agrega los operadores concatenacion
    def CreateConcat(self, expresion):
        new = ''
        operators = ['*','|','(']
        cont = 0
        while cont < len(expresion):
            if cont+1 >= len(expresion):
                new += expresion[-1]
                break

            if expresion[cont] == '*' and not (expresion[cont+1] in operators) and expresion[cont+1] != ')':
                new += expresion[cont]+'~'
            elif expresion[cont] == '*' and expresion[cont+1] == '(':
                new += expresion[cont]+'~'
            elif expresion[cont] == '?' and not (expresion[cont+1] in operators) and expresion[cont+1] != ')':
                new += expresion[cont]+'~'
            elif expresion[cont] == '?' and expresion[cont+1] == '(':
                new += expresion[cont]+'~'
            elif not (expresion[cont] in operators) and expresion[cont+1] == ')':
                new += expresion[cont]
            elif (not (expresion[cont] in operators) and not (expresion[cont+1] in operators)) or (not (expresion[cont] in operators) and (expresion[cont+1] == '(')):
                new += expresion[cont]+'~'
            else:
                new += expresion[cont]
        
            cont += 1
        return new

    # Crea las transiciones del grafo
    def create_transitions(self):
        f = {}
        for t in self.transiciones:
            i, s, fi = [*t]

            if i not in f.keys():
                f[i] = {}
            f[i][s] = fi

        return f

    # Genera los nodos y transiciones para el AFD
    def create_dfa(self):
        s0 = self.root.first_pos
        s0_dfa = DFA_Node(self.get_name(), s0, True)
        self.estados.append(s0_dfa)
        self.estado_inicial = s0_dfa.name

        interseccion = self.intersection(self.estado_final, [u for u in s0_dfa.conjunto_nodos])
        if len(interseccion) > 0:
            self.estados_aceptacion.append((s0_dfa.name, interseccion[0]))

        while not self.marked_state():
            T = self.get_unmarked_state()
            
            T.Mark()

            for s in self.simbolos:
                fp = []
                
                for u in T.conjunto_nodos:
                    if self.get_leaf(u).name == s:
                        fp += self.follow_pos[u]
                fp = {a for a in fp}
                fp = [a for a in fp]
                if len(fp) == 0:
                    continue

                U = DFA_Node(self.get_name(), fp, True)

                if U.id not in [n.id for n in self.estados]:
                    interseccion = self.intersection(self.estado_final, [u for u in U.conjunto_nodos])
                    if len(interseccion) > 0:
                        self.estados_aceptacion.append((U.name, interseccion[0]))
                    
                    self.estados.append(U)
                    self.transiciones.append((T.name, s, U.name))
                else:
                    self.count -= 1
                    for estado in self.estados:
                        if U.id == estado.id:
                            self.transiciones.append((T.name, s, estado.name))

        self.nombres_estados = dict(self.estados_aceptacion)

    def Simulate_DFA(self, exp, posicion):
        S = self.estado_inicial
        token = ''
        hayaCoincidencia = True
        checkpoint = i = posicion
        estadoAceptacion = None
        while hayaCoincidencia and i < len(exp):
            S = self.MoveSimulation(S, exp[i])

            if S in [a[0] for a in self.estados_aceptacion]:
                checkpoint = i
                estadoAceptacion = dict(self.estados_aceptacion)[S]
            
            if S == None:
                hayaCoincidencia = False
            
            i += 1
        token = exp[posicion:checkpoint + 1]
        return token, checkpoint + 1, estadoAceptacion
        
    # Implementacion de Move para la simulacion
    def MoveSimulation(self, Nodo, symbol):
        move = None
        for i in self.transiciones:
            if i[0] == Nodo and i[1] == symbol:
                move = i[2]

        return move

    # Obtiene la hoja a traves de su nombre
    def get_leaf(self, name):
        for n in self.nodos:
            if n.position == name:
                return n

    # Obtiene el estado unmarked
    def get_unmarked_state(self):
        for n in self.estados:
            if not n.isMarked:
                return n

    # Obtiene el nombre para asignarlo al nodo
    def get_name(self):
        if self.count == 0:
            self.count += 1
            return 'S'

        possible_names = ' ABCDEFGHIJKLMNOPQRTUVWXYZ'
        name = possible_names[self.count]
        self.count += 1

        if self.count == len(possible_names):
            self.rounds += 1
            self.count = 0

        return name * self.rounds

    # Se realiza el calculo de followpos
    def calculate_followpow(self):
        for n in self.nodos:
            if not n.is_operator and not n.nullable:
                self.add_followpos(n.position, [])

        for n in self.nodos:
            if n.name == '~':
                c1, c2 = [*n.children]

                for i in c1.last_pos:
                    self.add_followpos(i, c2.first_pos)

            elif n.name == '*':
                for i in n.last_pos:
                    self.add_followpos(i, n.first_pos)                

    # Revisa si existe algun estado desmarcado
    def marked_state(self):
        marks = [n.isMarked for n in self.estados]
        return functools.reduce(lambda a, b: a and b, marks)

    # Agrega un followpos
    def add_followpos(self, pos, val):
        if pos not in self.follow_pos.keys():
            self.follow_pos[pos] = []

        self.follow_pos[pos] += val
        self.follow_pos[pos] = {i for i in self.follow_pos[pos]}
        self.follow_pos[pos] = [i for i in self.follow_pos[pos]]

    # Convierte la expresion a una que pueda leer el programa
    def CleanExpression(self, regular):
        exp = []
        hasExpression = False
        hasPlus = False
        final = 0
        
        while ')?' in regular:
            real = []
            i = 0
            initial = []
            while i < len(regular) - 1:
                if regular[i] == '(':
                    initial.append(i)                        

                if regular[i] == ')':
                    real.append(regular[i])
                    if regular[i + 1] == '?':
                        final = i + 1
                        real.append('|')
                        real.append(epsilon)
                        real.append(')')
                        real.insert(initial[-1], '(')
                        i += 1
                        break
                    else:
                        initial.pop()

                else:
                    real.append(regular[i])
                i += 1

            regular = ''.join(real) + regular[i + 1:]

        regular_copy = regular

        if '?' in regular_copy:
            while '?' in regular_copy:
                i = regular_copy.find('?')
                symbol = regular_copy[i - 1]

                regular_copy = regular_copy.replace(symbol + '?', '(' + symbol + '|' + epsilon + ')')

        if regular_copy.count('(') > regular_copy.count(')'):
            for i in range(regular_copy.count('(') - regular_copy.count(')')):
                regular_copy += ')'

        elif regular_copy.count('(') < regular_copy.count(')'):
            for i in range(regular_copy.count(')') - regular_copy.count('(')):
                regular_copy = '(' + regular_copy

        return regular_copy

    # Obtiene el ultimo elemento guardado en el stack
    def peek(self, stack):
        return stack[-1] if stack else None

    # Determina si el token es un simbolo
    def is_symbol(self, s):
        digitos = self.simbolos_aceptables + [epsilon, '#']
        if s in digitos:
            return True
        return False

    # Obtiene el ID del nodo
    def get_id(self):
        self.id += 1
        return self.id

    # Implementacion de la creacion del arbol sintactico
    def apply_operator(self, operators, values):
        operator = operators.pop()
        right = values.pop()
        left = '@'

        if right not in self.simbolos and right != epsilon and right != '@' and right != '#':
            self.simbolos.append(right)

        if operator != '*' and operator != '?':
            left = values.pop()

            if left not in self.simbolos and left != epsilon and left != '@' and left != '#':
                self.simbolos.append(left)

        if operator == '|': return self.operator_or(left, right)
        elif operator == '~': return self.operator_concat(left, right)
        elif operator == '*': return self.operator_kleene(right)

    # Operacion kleen
    def operator_kleene(self, leaf):
        operator = '*'
        if isinstance(leaf, Leaf):
            root = Leaf(operator, None, True, [leaf], True)
            self.nodos += [root]
            return root

        else:
            id_left = None
            if leaf != epsilon:
                id_left = self.get_id()

            left_leaf = Leaf(leaf, id_left, False, [], False)
            root = Leaf(operator, None, True, [left_leaf], True)
            self.nodos += [left_leaf, root]

            return root

    # Operacion OR
    def operator_or(self, left, right):
        operator = '|'
        if isinstance(left, Leaf) and isinstance(right, Leaf):
            root = Leaf(operator, None, True, [left, right], left.nullable or right.nullable)
            self.nodos += [root]
            return root

        elif not isinstance(left, Leaf) and not isinstance(right, Leaf):
            id_left = None
            id_right = None
            if left != epsilon:
                id_left = self.get_id()
            if right != epsilon:
                id_right = self.get_id()

            left_leaf = Leaf(left, id_left, False, [], False)
            right_leaf = Leaf(right, id_right, False, [], False)
            root = Leaf(operator, None, True, [left_leaf, right_leaf], left_leaf.nullable or right_leaf.nullable)

            self.nodos += [left_leaf, right_leaf, root]

            return root

        elif isinstance(left, Leaf) and not isinstance(right, Leaf):
            id_right = None
            if right != epsilon:
                id_right = self.get_id()
            
            right_leaf = Leaf(right, id_right, False, [], False)
            root = Leaf(operator, None, True, [left, right_leaf], left.nullable or right_leaf.nullable)

            self.nodos += [right_leaf, root]
            return root

        elif not isinstance(left, Leaf) and isinstance(right, Leaf):
            id_left = None
            if left != epsilon:
                id_left = self.get_id()
            
            left_leaf = Leaf(left, id_left, False, [], False)
            root = Leaf(operator, None, True, [left_leaf, right], left_leaf.nullable or right.nullable)

            self.nodos += [left_leaf, root]
            return root

    # Operacion concatenacion
    def operator_concat(self, left, right):
        operator = '~'
        if isinstance(left, Leaf) and isinstance(right, Leaf):
            root = Leaf(operator, None, True, [left, right], left.nullable and right.nullable)
            self.nodos += [root]
            return root

        elif not isinstance(left, Leaf) and not isinstance(right, Leaf):
            id_left = None
            id_right = None
            if left != epsilon:
                id_left = self.get_id()
            if right != epsilon:
                id_right = self.get_id()

            left_leaf = Leaf(left, id_left, False, [], False)
            right_leaf = Leaf(right, id_right, False, [], False)
            root = Leaf(operator, None, True, [left_leaf, right_leaf], left_leaf.nullable and right_leaf.nullable)

            self.nodos += [left_leaf, right_leaf, root]
            return root

        elif isinstance(left, Leaf) and not isinstance(right, Leaf):
            id_right = None
            if right != epsilon:
                id_right = self.get_id()
            
            right_leaf = Leaf(right, id_right, False, [], False)
            root = Leaf(operator, None, True, [left, right_leaf], left.nullable and right_leaf.nullable)

            self.nodos += [right_leaf, root]
            return root
        
        elif not isinstance(left, Leaf) and isinstance(right, Leaf):
            id_left = None
            if left != epsilon:
                id_left = self.get_id()
            
            left_leaf = Leaf(left, id_left, False, [], False)
            root = Leaf(operator, None, True, [left_leaf, right], left_leaf.nullable and right.nullable)

            self.nodos += [left_leaf, root]
            return root

    # Obtiene la precedencia entre dos operadores
    def greater_precedence(self, op1, op2):
        precedences = {'|' : 0, '~' : 1, '*' : 2}
        return precedences[op1] >= precedences[op2]
    
    # Implementacion de la creacion del arbol sintactico
    def evaluate(self, expression):
        values = []
        operators = []
        for token in expression:
            if self.is_symbol(token):
                values.append(token)

            elif token == '(':
                operators.append(token)

            elif token == ')':
                top = self.peek(operators)

                while top is not None and top != '(':
                    raiz = self.apply_operator(operators, values)
                    values.append(raiz)
                    top = self.peek(operators)
                operators.pop()

            else:
                top = self.peek(operators)

                while top is not None and top not in '()' and self.greater_precedence(top, token):
                    raiz = self.apply_operator(operators, values)
                    values.append(raiz)
                    top = self.peek(operators)
                operators.append(token)

        while self.peek(operators) is not None:
            raiz = self.apply_operator(operators, values)
            values.append(raiz)
        self.root = values.pop()
            
class Leaf():
    def __init__(self, name, position, is_operator, children, nullable):
        self.name = name
        self.position = position
        self.is_operator = is_operator
        self.children = children
        self.nullable = nullable

        self.first_pos = []
        self.last_pos = []
        self.follow_pos = []

        if self.name == epsilon:
            self.nullable = True

        self.AddFirstPos()
        self.AddLastPos()

    # Obtiene el nombre de la hoja
    def GetName(self):
        return f'{self.name} - {self.position}'

    # Agrega el firstpos de la hoja
    def AddFirstPos(self):
        if self.is_operator:
            if self.name == '|':
                self.first_pos = self.children[0].first_pos + self.children[1].first_pos
            elif self.name == '~':
                if self.children[0].nullable:
                    self.first_pos = self.children[0].first_pos + self.children[1].first_pos
                else:
                    self.first_pos += self.children[0].first_pos
            elif self.name == '*':
                self.first_pos += self.children[0].first_pos
        else:
            if self.name != epsilon:
                self.first_pos.append(self.position)

    # Agrega el lastpos de la hoja
    def AddLastPos(self):
        if self.is_operator:
            if self.name == '|':
                self.last_pos = self.children[0].last_pos + self.children[1].last_pos
            elif self.name == '~':
                if self.children[1].nullable:
                    self.last_pos = self.children[0].last_pos + self.children[1].last_pos
                else:
                    self.last_pos += self.children[1].last_pos
            elif self.name == '*':
                self.last_pos += self.children[0].last_pos
        else:
            if self.name != epsilon:
                self.last_pos.append(self.position)

tokens = {
''' + r'{}'.format(tokens_program) + '''}

exceptions = {
''' + f'{exception_program}' + '''}

acceptable_characters = []
for k, v in tokens.items():
    for i in v:
        if i not in '()|?*~' and i not in acceptable_characters:
            acceptable_characters.append(i)

exp = '|'.join(['((' + token + ')#)' for token in tokens.values()])

archivo = input('Ingrese el nombre del archivo a escanear: ')
filee = open(archivo, 'r', encoding='utf-8')
w = ''.join(filee.readlines())

# ------------------------- METODO DIRECTO ---------------------------------------------

syntax = SyntaxTree(exp, acceptable_characters, [t for t in tokens.keys()])

states = {s.name for s in syntax.estados}
initial_state = syntax.estado_inicial
accepting_state = {s[0] for s in syntax.estados_aceptacion}
alphabet = {a for a in syntax.simbolos}
transition_function = syntax.create_transitions()
alphabet, alphabet_print = utilities.getAlphabet(transition_function)

utilities.graph_automata(states, alphabet, initial_state, accepting_state, transition_function, 'grafos/DIRECT_AFD')

print('')
print('----------------------------------------------------------------------')
pos = 0
while pos < len(w):
    resultado, pos, aceptacion = syntax.Simulate_DFA(w, pos)
    if aceptacion:
        permitido = True
        for excepcion in exceptions[syntax.tokens[aceptacion]].keys():
            if resultado == excepcion:
                permitido = False
                print('     >', repr(excepcion), 'es el keyword', exceptions[syntax.tokens[aceptacion]][excepcion], '<')
                break

        if permitido:
            print('     >', repr(resultado), 'es', syntax.tokens[aceptacion], '<')
    else:
        print('     >', repr(resultado), 'es un simbolo NO esperado', '<')
print('----------------------------------------------------------------------')
print('')
'''

f = open('scanner.py', 'w', encoding='utf-8')
f.write(programa_completo)
f.close()
