tabla_simbolos = {}

def verificar_tipo(nodo):
    if isinstance(nodo, tuple):
        print(f"Procesando nodo: {nodo}")

        # Si el nodo es un programa
        if nodo[0] == 'programa':
            # Procesamos declaraciones
            for decl in nodo[1]:
                resultado_decl = verificar_tipo(decl)
                if resultado_decl[0] == 'error':
                    return resultado_decl
            # Procesamos sentencias
            for sent in nodo[2]:
                resultado_sent = verificar_tipo(sent)
                if resultado_sent[0] == 'error':
                    return resultado_sent
            return ('programa', 'ok', nodo)

        # Si el nodo es una declaración de variable
        if nodo[0] == 'decl':
            tipo = nodo[1]
            for var in nodo[2]:
                tabla_simbolos[var] = tipo
            return ('decl', tipo, nodo[2])

        # Si es una asignación
        elif nodo[0] == 'assign':
            var = nodo[1]
            exp = verificar_tipo(nodo[2])
            tipo_var = tabla_simbolos.get(var, None)
            if tipo_var is None:
                return ('error', f"Variable '{var}' no está declarada.")
            if tipo_var != exp[1]:
                return ('error', f"Error de tipos: Se esperaba {tipo_var} pero se encontró {exp[1]}")
            return ('assign', tipo_var, var, exp)

        # Si es una operación aritmética
        elif nodo[0] in ('+', '-', '*', '/'):
            tipo_izq = verificar_tipo(nodo[1])
            tipo_der = verificar_tipo(nodo[2])
            if tipo_izq[1] != tipo_der[1]:
                return ('error', f"Error de tipos: {tipo_izq[1]} incompatible con {tipo_der[1]}")
            return (nodo[0], tipo_izq[1], tipo_izq, tipo_der)

        # Si es una condición if-else
        elif nodo[0] == 'if_else':
            condicion = verificar_tipo(nodo[1])
            if condicion[1] != 'bool':
                return ('error', "Condición en 'if' debe ser booleana.")
            bloque_then = verificar_tipo(nodo[2])
            bloque_else = verificar_tipo(nodo[3])
            return ('if_else', condicion, bloque_then, bloque_else)

        # Si es un ciclo while
        elif nodo[0] == 'while':
            condicion = verificar_tipo(nodo[1])
            if condicion[1] != 'bool':
                return ('error', "Condición en 'while' debe ser booleana.")
            cuerpo = verificar_tipo(nodo[2])
            return ('while', condicion, cuerpo)

        # Si es un ciclo do-while, ajustamos el formato para mostrar más ordenadamente
        elif nodo[0] == 'do_until':
            cuerpo = verificar_tipo(nodo[1])
            condicion = verificar_tipo(nodo[2])
            if condicion[1] != 'bool':
                return ('error', "Condición en 'do_until' debe ser booleana.")
            return ('do_until', 'bloque', cuerpo, 'condición', condicion)

        # Si es una operación lógica
        elif nodo[0] in ('and', 'or'):
            tipo_izq = verificar_tipo(nodo[1])
            tipo_der = verificar_tipo(nodo[2])
            if tipo_izq[1] != 'bool' or tipo_der[1] != 'bool':
                return ('error', f"Error de tipos: Se esperaba 'bool' en una operación lógica.")
            return (nodo[0], 'bool', tipo_izq, tipo_der)

        # Si es una operación de comparación
        elif nodo[0] in ('==', '!=', '<', '>', '<=', '>='):
            tipo_izq = verificar_tipo(nodo[1])
            tipo_der = verificar_tipo(nodo[2])
            if tipo_izq[1] != tipo_der[1]:
                return ('error', f"Error de tipos: Comparación entre {tipo_izq[1]} y {tipo_der[1]}.")
            return (nodo[0], 'bool', tipo_izq, tipo_der)

    # Si es un literal booleano (true o false)
    elif nodo in ('true', 'false'):
        return ('literal', 'bool', nodo)

    # Si es un número
    elif isinstance(nodo, (int, float)):
        tipo = 'int' if isinstance(nodo, int) else 'float'
        return ('numero', tipo, nodo)

    # Si es un identificador (variable)
    elif isinstance(nodo, str):
        tipo = tabla_simbolos.get(nodo, "undefined")
        if tipo == "undefined":
            return ('error', f"Variable '{nodo}' no está declarada.")
        return ('var', tipo, nodo)

    return ('error', f"Nodo no reconocido: {nodo}")

def analizar_semantico(arbol):
    try:
        resultado = verificar_tipo(arbol)
        if resultado[0] == 'error':
            return resultado
        return resultado
    except Exception as e:
        return ('error', str(e))
