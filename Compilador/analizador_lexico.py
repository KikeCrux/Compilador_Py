import ply.lex as lex

# Definir las palabras reservadas
reserved = {
    'main': 'MAIN',
    'bool': 'BOOL',
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR',
    'if': 'IF',
    'else': 'ELSE',
    'fi': 'FI',
    'while': 'WHILE',
    'do': 'DO',
    'until': 'UNTIL',
    'read': 'READ',
    'write': 'WRITE',
    'true': 'TRUE',
    'false': 'FALSE',
    'and': 'AND',
    'or': 'OR',
    'then': 'THEN',
    'break': 'BREAK'
}

# Definir los tokens del lexer
tokens = (
    'ID',
    'NUMBERINT',
    'NUMBERFLOAT',
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
    'NOT'
) + tuple(reserved.values())

# Expresiones regulares para los tokens simples
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

# Calcular la columna de un token
def find_column(input_text, token):
    last_cr = input_text.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = -1
    return token.lexpos - last_cr

# Manejar identificadores y palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Chequeo de palabras reservadas
    t.lineno = t.lexer.lineno  # Asignar la línea al token
    t.column = find_column(t.lexer.lexdata, t)  # Calcular la columna
    return t

# Manejar números (flotantes)
def t_NUMBERFLOAT(t):
    r'\d+(\.\d+)'
    t.value = float(t.value)
    t.column = find_column(t.lexer.lexdata, t)  # Calcular la columna
    return t

# Manejar números (enteros)
def t_NUMBERINT(t):
    r'\d+'
    t.value = int(t.value)
    t.column = find_column(t.lexer.lexdata, t)  # Calcular la columna
    return t

# Ignorar comentarios de una sola línea (// ...)
def t_COMMENT_SINGLELINE(t):
    r'//.*'
    pass  # Ignorar el comentario

# Ignorar comentarios de múltiples líneas (/* ... */)
def t_COMMENT_MULTILINE(t):
    r'/\*[\s\S]*?\*/'
    pass  # Ignorar el comentario

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Manejar nuevas líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)  # Actualizar número de línea

# Manejar errores de caracteres ilegales
def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}' en la línea {t.lexer.lineno}, columna {find_column(t.lexer.lexdata, t)}")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

# Función que realiza el análisis léxico después de limpiar el texto
def analizar_lexico(texto):
    texto = limpiar_espacios_invisibles(texto)
    lexer.lineno = 1  # Reiniciar el número de línea
    lexer.input(texto)  # Usar el método input de la instancia del lexer
    tokens = []
    while True:
        token = lexer.token()
        if not token:
            break
        token.column = find_column(lexer.lexdata, token)  # Asegurarse de que todos los tokens tengan columna
        tokens.append(token)
        # Imprimir el valor del token, la línea y la columna
    return tokens

# Función para reemplazar espacios no separadores (U+00A0) por espacios normales
def limpiar_espacios_invisibles(texto):
    return texto.replace('\u00A0', ' ')
