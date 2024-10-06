# analizador_semantico.py

# Tabla de símbolos para almacenar los tipos de las variables
tabla_simbolos = {}

# Función para verificar los tipos en el árbol sintáctico
def verificar_tipo(nodo):
    if isinstance(nodo, tuple):
        # Declaración de variable
        if nodo[0] == 'decl':
            tipo = nodo[1]
            for var in nodo[2]:
                tabla_simbolos[var] = tipo
            return f'Declaración de {tipo} para variables {nodo[2]}'
        
        # Asignación de valor a una variable
        if nodo[0] == 'assign':
            var = nodo[1]
            exp = verificar_tipo(nodo[2])
            tipo_var = tabla_simbolos.get(var, None)
            if tipo_var is None:
                raise Exception(f"Error: Variable '{var}' no está declarada.")
            if tipo_var != exp:
                raise Exception(f"Error de tipos: Se esperaba {tipo_var} pero se encontró {exp}")
            return tipo_var

        # Operaciones aritméticas
        if nodo[0] in ('+', '-', '*', '/'):
            tipo_izq = verificar_tipo(nodo[1])
            tipo_der = verificar_tipo(nodo[2])
            if tipo_izq != tipo_der:
                raise Exception(f"Error de tipos: {tipo_izq} incompatible con {tipo_der}")
            return tipo_izq
        
        # Retorno de tipo de número
        if isinstance(nodo, (int, float)):
            return 'int' if isinstance(nodo, int) else 'float'

    # Identificadores (variables)
    elif isinstance(nodo, str):
        return tabla_simbolos.get(nodo, "undefined")

    return None

# Recorrer el árbol y verificar los tipos en cada nodo
def analizar_semantico(arbol):
    try:
        return verificar_tipo(arbol)
    except Exception as e:
        return str(e)
