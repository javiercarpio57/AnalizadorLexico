
import functools
import automata
epsilon = 'ε'

tokens = {
"ident":'˂A∪B∪C∪D∪E∪F∪G∪H∪I∪J∪K∪L∪M∪N∪O∪P∪Q∪R∪S∪T∪U∪V∪W∪X∪Y∪Z∪a∪b∪c∪d∪e∪f∪g∪h∪i∪j∪k∪l∪m∪n∪o∪p∪q∪r∪s∪t∪u∪v∪w∪x∪y∪z˃˂˂A∪B∪C∪D∪E∪F∪G∪H∪I∪J∪K∪L∪M∪N∪O∪P∪Q∪R∪S∪T∪U∪V∪W∪X∪Y∪Z∪a∪b∪c∪d∪e∪f∪g∪h∪i∪j∪k∪l∪m∪n∪o∪p∪q∪r∪s∪t∪u∪v∪w∪x∪y∪z˃∪˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9˃˃Δ',
"number":'˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9˃˂˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9˃˃Δ',
}

exceptions = {
"ident": {'while': 'while', 'do': 'do', 'if': 'if', 'switch': 'switch'},
"number": {},
}

ignores = []

acceptable_characters = []
for k, v in tokens.items():
    for i in v:
        if i not in '˂˃∪ƷΔ∩' and i not in acceptable_characters:
            acceptable_characters.append(i)

exp = '∪'.join(['˂˂' + token + '˃∫˃' for token in tokens.values()])

archivo = input('Ingrese el nombre del archivo a escanear: ')
filee = open(archivo, 'r', encoding='utf-8', errors='replace')
w = ''.join(filee.readlines())

# ------------------------- METODO DIRECTO ---------------------------------------------

syntax = automata.SyntaxTree(exp, acceptable_characters, [t for t in tokens.keys()])

print('')
print('----------------------------------------------------------------------')
pos = 0
while pos < len(w):
    resultado, pos, aceptacion = syntax.Simulate_DFA(w, pos, ignores)
    if aceptacion:
        permitido = True
        for excepcion in exceptions[syntax.tokens[aceptacion]].keys():
            if resultado == excepcion:
                permitido = False
                print('     >', repr(excepcion), 'es el keyword', exceptions[syntax.tokens[aceptacion]][excepcion], '<')
                break

        if permitido:
            if syntax.tokens[aceptacion] not in ignores:
                print('     >', repr(resultado), 'es', syntax.tokens[aceptacion], '<')
    else:
        if resultado != '':
            print('     >', repr(resultado), 'es un simbolo NO esperado', '<')
print('----------------------------------------------------------------------')
print('')
