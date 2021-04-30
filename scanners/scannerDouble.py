
import functools
import automata
epsilon = 'ε'

tokens = {
"number":'˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9˃˂˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9˃˃Δ',
"decnumber":'˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9˃˂˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9˃˃Δ˂.˃˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9˃˂˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9˃˃Δ',
"white":'˂\n∪\r∪\t∪ ˃˂˂\n∪\r∪\t∪ ˃˃Δ',
}

exceptions = {
"number": {},
"decnumber": {},
"white": {},
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
