import ply.lex as lex

# Definir las palabras reservadas
reserved = {
    'program': 'PROGRAM',
    'bool': 'BOOL',
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR',
    'byte': 'BYTE',
    'long': 'LONG',
    'double': 'DOUBLE',
    'if': 'IF',
    'else': 'ELSE',
    'fi': 'FI',
    'while': 'WHILE',
    'do': 'DO',
    'until': 'UNTIL',
    'read': 'READ',
    'write': 'WRITE',
    'break': 'BREAK',
    'try': 'TRY',
    'return': 'RETURN',
    'void': 'VOID',
    'public': 'PUBLIC',
    'protected': 'PROTECTED',
    'private': 'PRIVATE',
    'class': 'CLASS',
    'abstract': 'ABSTRACT',
    'interface': 'INTERFACE',
    'this': 'THIS',
    'friend': 'FRIEND',
    'true': 'TRUE',
    'false': 'FALSE',
    'then': 'THEN',
    'and': 'AND',
    'or': 'OR'
}

# Definir las reglas del lexer
tokens = (
    'ID',
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'EQUALS',
    'SEMICOLON',
    'COMMA',
    'LBRACE',
    'RBRACE',
    'LT',
    'GT',
    'LE',
    'GE',
    'EQ',
    'NE',
    'NOT',
    'PLUS_EQUALS',
    'MINUS_EQUALS',
    'STRING',
    'COMMENT'
) + tuple(reserved.values())

# Expresiones regulares para los tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'='
t_SEMICOLON = r';'
t_COMMA = r','
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_EQ = r'=='
t_NE = r'!='
t_NOT = r'!'
t_PLUS_EQUALS = r'\+='
t_MINUS_EQUALS = r'-='
t_STRING = r'\"([^\\\n]|(\\.))*?\"'

# Manejo de comentarios
def t_COMMENT(t):
    r'(//.*)|(/\*(.|\n)*?\*/)'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

# Ignorar espacios, tabulaciones y nuevas líneas
t_ignore = ' \t'

# Función para manejar nuevas líneas y actualizar el número de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejar errores de tokens
def t_error(t):
    print("Caracter ilegal '%s'" % t.value[0])
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

# Función para reemplazar espacios no separadores (U+00A0) por espacios normales
def limpiar_espacios_invisibles(texto):
    return texto.replace('\u00A0', ' ')

# Función que realiza el análisis léxico después de limpiar el texto
def analizar_lexico(texto):
    texto = limpiar_espacios_invisibles(texto)
    lexer.lineno = 1
    lexer.input(texto)
    tokens = []
    while True:
        token = lexer.token()
        if not token:
            break
        tokens.append(token)
    return tokens