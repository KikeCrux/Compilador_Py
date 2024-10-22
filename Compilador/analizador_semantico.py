# Inicialización de la tabla de símbolos
tabla_simbolos = {}

# Primera pasada para construir la tabla de símbolos, incluyendo la línea de declaración
def construir_tabla_simbolos(nodo, tabla_simbolos, linea=1):
    if isinstance(nodo, tuple):
        if nodo[0] == 'decl':
            tipo = nodo[1]
            for var in nodo[2]:
                if var.strip():
                    if var in tabla_simbolos:
                        print(f"Error semántico: La variable '{var}' ya fue declarada en la línea {tabla_simbolos[var]['lineas'][0]}.")
                    else:
                        tabla_simbolos[var] = {'tipo': tipo, 'valor': None, 'lineas': [linea]}
        else:
            for decl in nodo:
                construir_tabla_simbolos(decl, tabla_simbolos, linea)
    elif isinstance(nodo, str):
        if nodo in tabla_simbolos:
            tabla_simbolos[nodo]['lineas'].append(linea)
    elif isinstance(nodo, list):
        for node in nodo:
            construir_tabla_simbolos(node, tabla_simbolos, linea)

# Segunda pasada para evaluar expresiones y asignaciones
def verificar_tipo(nodo, tabla_simbolos, linea=0):
    try:
        if isinstance(nodo, tuple):
            if isinstance(nodo[-1], int):
                linea = nodo[-1]

            if nodo[0] == 'main':
                declaraciones = []
                sentencias = []
                for decl in nodo[1]:
                    resultado_decl = verificar_tipo(decl, tabla_simbolos, linea)
                    declaraciones.append(resultado_decl)
                for sent in nodo[2]:
                    resultado_sent = verificar_tipo(sent, tabla_simbolos, linea)
                    sentencias.append(resultado_sent)
                return ('program', 'main', declaraciones, sentencias)

            elif nodo[0] == 'decl':
                tipo = nodo[1]
                variables = []
                for var in nodo[2]:
                    if var.strip():
                        tabla_simbolos[var] = {'tipo': tipo, 'valor': None, 'lineas': [linea]}
                        variables.append(f"{var}.{tipo}")
                return ('decl', f"listvar.{tipo}", variables)

            elif nodo[0] == 'assign':
                var = nodo[1]
                if var in tabla_simbolos:
                    tabla_simbolos[var]['lineas'].append(linea)
                exp = verificar_tipo(nodo[2], tabla_simbolos, linea)
                tipo_var = tabla_simbolos.get(var, None)
                if tipo_var is None:
                    return ('assign', 'error', f"Variable '{var}' no está declarada.", exp)

                valor = obtener_valor(exp, tabla_simbolos)
                tabla_simbolos[var]['valor'] = valor
                if linea not in tabla_simbolos[var]['lineas']:
                    tabla_simbolos[var]['lineas'].append(linea)
                return ('assign', f"{var}.{tipo_var['tipo']}", exp)

            elif nodo[0] in ('+', '-', '*', '/'):
                tipo_izq = verificar_tipo(nodo[1], tabla_simbolos, linea)
                tipo_der = verificar_tipo(nodo[2], tabla_simbolos, linea)

                if tipo_izq[0] == 'error' or tipo_der[0] == 'error':
                    return ('error', f"Error en operandos de la operación {nodo[0]}")

                valor_izq = obtener_valor(tipo_izq, tabla_simbolos)
                valor_der = obtener_valor(tipo_der, tabla_simbolos)

                if isinstance(valor_izq, (int, float)) and isinstance(valor_der, (int, float)):
                    if nodo[0] == '+':
                        resultado = valor_izq + valor_der
                    elif nodo[0] == '-':
                        resultado = valor_izq - valor_der
                    elif nodo[0] == '*':
                        resultado = valor_izq * valor_der
                    elif nodo[0] == '/':
                        if valor_der == 0:
                            return ('error', "División por cero", nodo)
                        # Evaluamos si ambos son int para forzar una división entera
                        resultado = valor_izq // valor_der if isinstance(valor_izq, int) and isinstance(valor_der, int) else valor_izq / valor_der

                    tipo_resultado = 'int' if isinstance(resultado, int) else 'float'
                    return (nodo[0], f"{int(resultado) if tipo_resultado == 'int' else resultado}.{tipo_resultado}.val", [tipo_izq, tipo_der])
                else:
                    return ('error', f"Error en la operación {nodo[0]}: tipos incompatibles {tipo_izq} y {tipo_der}")

            elif nodo[0] in ('>', '<', '>=', '<=', '==', '!='):
                izq = verificar_tipo(nodo[1], tabla_simbolos, linea)
                der = verificar_tipo(nodo[2], tabla_simbolos, linea)
                if izq[0] == 'error' or der[0] == 'error':
                    return ('error', f"Error en operandos de la relación {nodo[0]}")

                valor_izq = obtener_valor(izq, tabla_simbolos)
                valor_der = obtener_valor(der, tabla_simbolos)

                resultado = eval(f"{valor_izq} {nodo[0]} {valor_der}")
                return (nodo[0], f"{resultado}.bool", [izq, der])
            else:
                results = []
                for node in nodo[1:]:
                    results.append(verificar_tipo(node, tabla_simbolos, linea))
                return (nodo[0], 'sentencia', results)

        elif isinstance(nodo, (int, float)):
            tipo = 'int' if isinstance(nodo, int) else 'float'
            return ('numero', f"{tipo}", f"{nodo}.{tipo}.val")

        elif isinstance(nodo, str):
            if nodo in tabla_simbolos:
                tabla_simbolos[nodo]['lineas'].append(linea)
                tipo = tabla_simbolos.get(nodo, "undefined")
                if tipo != "undefined":
                    if tipo['tipo'] in ['int', 'float']:
                        return ('var', f"{tipo['tipo']}", f"{nodo}.{tipo['tipo']}.val")
                    else:
                        return ('var', f"{tipo['tipo']}", f"{nodo}.{tipo['tipo']}")

        elif isinstance(nodo, list):
            results = []
            for node in nodo:
                result = verificar_tipo(node, tabla_simbolos, linea)
                results.append(result)
            return ('lista', 'sentencia', results)

    except Exception as e:
        print(f"Error manejado: {e}", nodo)
        return ('error', f"Error en la operación: {str(e)}", nodo)

def obtener_valor(nodo, tabla_simbolos):
    if nodo[0] == "numero":
        num_str = nodo[2].split('.')[0]
        tipo = nodo[1]
        return int(num_str) if tipo == 'int' else float(num_str)
    elif nodo[0] == 'var':
        var_name = nodo[2].split('.')[0]
        tipo_var = tabla_simbolos.get(var_name, None)
        if tipo_var:
            valor = tipo_var['valor']
            if valor is not None:
                return valor
            else:
                raise ValueError(f"Variable '{var_name}' no tiene valor asignado")
        else:
            raise ValueError(f"Variable '{var_name}' no está definida")
    elif nodo[0] in ('+', '-', '*', '/'):
        valor_izq = obtener_valor(nodo[2][0], tabla_simbolos)
        valor_der = obtener_valor(nodo[2][1], tabla_simbolos)
        if nodo[0] == '+':
            return valor_izq + valor_der
        elif nodo[0] == '-':
            return valor_izq - valor_der
        elif nodo[0] == '*':
            return valor_izq * valor_der
        elif nodo[0] == '/':
            if valor_der == 0:
                raise ZeroDivisionError("División por cero")
            if isinstance(valor_izq, int) and isinstance(valor_der, int):
                return valor_izq // valor_der
            else:
                return valor_izq / valor_der
    elif nodo[0] in ('>', '<', '>=', '<=', '==', '!='):
        valor_izq = obtener_valor(nodo[2][0], tabla_simbolos)
        valor_der = obtener_valor(nodo[2][1], tabla_simbolos)
        return eval(f"{valor_izq} {nodo[0]} {valor_der}")
    return None

# Función para mostrar el árbol semántico sin detenerse ante errores
def analizar_semantico(arbol, tabla_simbolos):
    try:
        resultado = verificar_tipo(arbol, tabla_simbolos)
        return resultado
    except Exception as e:
        return ('error', str(e))

# Función para imprimir el árbol de manera legible y manejar visualización de int/int como int
def imprimir_arbol(arbol, nivel=0):
    if isinstance(arbol, tuple):
        # Si es una operación de división, verificar si ambos operandos son int
        if arbol[0] == '/' and '.int.val' in arbol[1]:
            # Si ambos son int, forzar visualización como int y truncar resultado
            print("  " * nivel + f"/: {arbol[1]}")  # Mostramos el resultado como int
        elif arbol[0] in ('+', '-', '*', '/'):
            print("  " * nivel + f"{arbol[0]}: {arbol[1]}")
        else:
            print("  " * nivel + str(arbol[0]))

        if len(arbol) > 2:
            for subarbol in arbol[2]:
                imprimir_arbol(subarbol, nivel + 1)
    else:
        print("  " * nivel + str(arbol))

# Probar el programa
def analizar_programa(codigo):
    resultado_semantico = analizar_semantico(codigo, tabla_simbolos)
    imprimir_arbol(resultado_semantico)