tabla_simbolos = {}

def verificar_tipo(nodo):
    if isinstance(nodo, tuple):
        print(f"Procesando nodo: {nodo}")

        # Si el nodo es un programa
        if nodo[0] == 'main':
            # Procesamos declaraciones
            declaraciones = []
            for decl in nodo[1]:
                resultado_decl = verificar_tipo(decl)
                declaraciones.append(resultado_decl)
                if resultado_decl[0] == 'error':
                    declaraciones.append(('error', f"Error en la declaración {decl}"))
            # Procesamos sentencias
            sentencias = []
            for sent in nodo[2]:
                resultado_sent = verificar_tipo(sent)
                sentencias.append(resultado_sent)
                if resultado_sent[0] == 'error':
                    sentencias.append(('error', f"Error en la sentencia {sent}"))
            return ('main', 'ok', declaraciones, sentencias)

        # Si el nodo es una declaración de variable
        if nodo[0] == 'decl':
            tipo = nodo[1]
            variables = []
            for var in nodo[2]:
                if var.strip():  # Verificar que la variable no esté vacía
                    tabla_simbolos[var] = tipo
                    variables.append(f"{var}.{tipo}")  # Añadir el atributo var.tipo
            return ('decl', f"listvar.{tipo}", variables)

        # Si es una asignación
        elif nodo[0] == 'assign':
            var = nodo[1]
            exp = verificar_tipo(nodo[2])
            tipo_var = tabla_simbolos.get(var, None)
            if tipo_var is None:
                return ('assign', 'error', f"Variable '{var}' no está declarada.", exp)
            if tipo_var != exp:
                return ('assign', 'error', f"Error de tipos: Se esperaba {tipo_var} pero se encontró {exp}", exp)
            return ('assign', f"{var}.{tipo_var}", var)

        # Si es una operación aritmética
        elif nodo[0] in ('+', '-', '*', '/'):
            tipo_izq = verificar_tipo(nodo[1])
            tipo_der = verificar_tipo(nodo[2])
            if tipo_izq != tipo_der:
                return (nodo[0], 'error', f"Error de tipos: {tipo_izq} incompatible con {tipo_der}", tipo_izq, tipo_der)
            return (nodo[0], f"{tipo_izq}", tipo_izq, tipo_der)

        # Si es una condición if-else
        elif nodo[0] == 'if_else':
            condicion = verificar_tipo(nodo[1])
            if condicion != 'bool':
                return ('if_else', 'error', "Condición en 'if' debe ser booleana.", condicion)
            bloque_then = verificar_tipo(nodo[2])
            bloque_else = verificar_tipo(nodo[3])
            return ('if_else', condicion, bloque_then, bloque_else)

        # Si es un ciclo while
        elif nodo[0] == 'while':
            condicion = verificar_tipo(nodo[1])
            if condicion != 'bool':
                return ('while', 'error', "Condición en 'while' debe ser booleana.", condicion)
            cuerpo = verificar_tipo(nodo[2])
            return ('while', condicion, cuerpo)

        # Si es un ciclo do-while, ajustamos el formato para mostrar más ordenadamente
        elif nodo[0] == 'do_until':
            cuerpo = verificar_tipo(nodo[1])
            condicion = verificar_tipo(nodo[2])
            if condicion != 'bool':
                return ('do_until', 'error', "Condición en 'do_until' debe ser booleana.", cuerpo, condicion)
            return ('do_until', 'bloque', cuerpo, condicion)

        # Si es una operación lógica
        elif nodo[0] in ('and', 'or'):
            tipo_izq = verificar_tipo(nodo[1])
            tipo_der = verificar_tipo(nodo[2])
            if tipo_izq != 'bool' or tipo_der != 'bool':
                return (nodo[0], 'error', f"Error de tipos: Se esperaba 'bool' en una operación lógica.", tipo_izq, tipo_der)
            return (nodo[0], 'bool', tipo_izq, tipo_der)

        # Si es una operación de comparación
        elif nodo[0] in ('==', '!=', '<', '>', '<=', '>='):
            tipo_izq = verificar_tipo(nodo[1])
            tipo_der = verificar_tipo(nodo[2])
            if tipo_izq != tipo_der:
                return (nodo[0], 'error', f"Error de tipos: Comparación entre {tipo_izq} y {tipo_der}.", tipo_izq, tipo_der)
            return (nodo[0], 'bool', tipo_izq, tipo_der)

    # Si es un literal booleano (true o false)
    elif nodo in ('true', 'false'):
        return 'bool'

    # Si es un número
    elif isinstance(nodo, (int, float)):
        tipo = 'int' if isinstance(nodo, int) else 'float'
        return tipo  # Subimos solo el tipo

    # Si es un identificador (variable)
    elif isinstance(nodo, str):
        tipo = tabla_simbolos.get(nodo, "undefined")
        if tipo == "undefined":
            return ('error', f"Variable '{nodo}' no está declarada.")
        return f"{nodo}.{tipo}"  # Concatenamos el nombre y el tipo

    return ('error', f"Nodo no reconocido: {nodo}")

# Función para mostrar el árbol semántico sin detenerse ante errores
def analizar_semantico(arbol):
    try:
        resultado = verificar_tipo(arbol)
        return resultado
    except Exception as e:
        return ('error', str(e))
