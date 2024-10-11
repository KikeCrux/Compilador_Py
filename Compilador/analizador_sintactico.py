import ply.yacc as yacc
from analizador_lexico import tokens, lexer

# Definir la gramática

def p_programa(p):
    '''programa : MAIN LBRACE lista_decl lista_sent RBRACE'''
    p[0] = ('main', p[3], p[4])

def p_lista_decl(p):
    '''lista_decl : lista_decl decl
                  | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_decl(p):
    '''decl : tipo lista_id SEMICOLON'''
    p[0] = ('decl', p[1], p[2])

def p_tipo(p):
    '''tipo : INT
            | FLOAT
            | BOOL'''
    p[0] = p[1]

def p_lista_id(p):
    '''lista_id : lista_id COMMA ID
                | ID'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_lista_sent(p):
    '''lista_sent : lista_sent sent
                  | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_sent(p):
    '''sent : sent_if
            | sent_while
            | sent_do
            | sent_read
            | sent_write
            | bloque
            | sent_assign
            | BREAK SEMICOLON'''
    if len(p) == 3 and p[1] == 'BREAK':
        p[0] = ('break',)
    else:
        p[0] = p[1]

def p_sent_if(p):
    '''sent_if : IF LPAREN exp_bool RPAREN THEN bloque ELSE bloque FI SEMICOLON
               | IF LPAREN exp_bool RPAREN THEN bloque FI SEMICOLON'''
    if len(p) == 10:
        p[0] = ('if_else', p[3], p[6], p[8])
    else:
        p[0] = ('if', p[3], p[6])

def p_sent_while(p):
    '''sent_while : WHILE LPAREN exp_bool RPAREN bloque'''
    p[0] = ('while', p[3], p[5])

def p_sent_do(p):
    '''sent_do : DO bloque UNTIL LPAREN exp_bool RPAREN SEMICOLON'''
    p[0] = ('do_until', p[2], p[5])

def p_sent_read(p):
    '''sent_read : READ ID SEMICOLON'''
    p[0] = ('read', p[2])

def p_sent_write(p):
    '''sent_write : WRITE exp_bool SEMICOLON'''
    p[0] = ('write', p[2])

def p_bloque(p):
    '''bloque : LBRACE lista_sent RBRACE'''
    p[0] = ('bloque', p[2])

def p_sent_assign(p):
    '''sent_assign : ID EQUALS exp_bool SEMICOLON'''
    p[0] = ('assign', p[1], p[3])

def p_exp_bool(p):
    '''exp_bool : exp_bool OR comb
                | comb'''
    if len(p) == 4:
        p[0] = ('or', p[1], p[3])
    else:
        p[0] = p[1]

def p_comb(p):
    '''comb : comb AND igualdad
            | igualdad'''
    if len(p) == 4:
        p[0] = ('and', p[1], p[3])
    else:
        p[0] = p[1]

def p_igualdad(p):
    '''igualdad : igualdad EQ rel
                | igualdad NE rel
                | rel'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_rel(p):
    '''rel : expr op_rel expr
           | expr'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_op_rel(p):
    '''op_rel : LT
              | LE
              | GT
              | GE'''
    p[0] = p[1]

def p_expr(p):
    '''expr : expr PLUS term
            | expr MINUS term
            | term'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_term(p):
    '''term : term TIMES unario
            | term DIVIDE unario
            | unario'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_unario(p):
    '''unario : NOT unario
              | MINUS unario
              | factor'''
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = p[1]

def p_factor(p):
    '''factor : NUMBER
              | ID
              | LPAREN exp_bool RPAREN
              | TRUE
              | FALSE'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_empty(p):
    '''empty :'''
    pass

# Mejorar la detección de errores de sintaxis
errores = []

def p_error(p):
    if p:
        columna = encontrar_columna(p)
        errores.append(f"Error de sintaxis en '{p.value}' en la línea {p.lineno}, columna {columna}")
        parser.errok()  # Recuperar de error para seguir analizando
    else:
        errores.append("Error de sintaxis en EOF (fin del archivo)")

def encontrar_columna(token):
    last_cr = lexer.lexdata.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = 0
    return token.lexpos - last_cr + 1

# Construir el parser
parser = yacc.yacc()

def analizar_sintactico(texto):
    global errores
    errores = []
    resultado = parser.parse(texto)
    return resultado, errores

def formatear_arbol(arbol, nivel=0):
    resultado = ""
    if isinstance(arbol, tuple):
        resultado += "  " * nivel + "(\n"
        resultado += "  " * (nivel + 1) + str(arbol[0]) + "\n"
        for elemento in arbol[1:]:
            resultado += formatear_arbol(elemento, nivel + 2) + "\n"
        resultado += "  " * nivel + ")"
    else:
        resultado += "  " * nivel + str(arbol)
    return resultado
