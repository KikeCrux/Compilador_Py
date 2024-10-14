# Inicialización de la tabla de símbolos
tabla_simbolos = {}

# Primera pasada para construir la tabla de símbolos, incluyendo la línea de declaración
def construir_tabla_simbolos(nodo, tabla_simbolos, linea=1):
    if isinstance(nodo, tuple):
        # Si el nodo es una declaración de variable
        if nodo[0] == 'decl':
            tipo = nodo[1]
            for var in nodo[2]:
                if var.strip():  # Verificar que la variable no esté vacía
                    if var in tabla_simbolos:
                        print(f"Error semántico: La variable '{var}' ya fue declarada en la línea {tabla_simbolos[var]['lineas'][0]}.")
                    else:
                        tabla_simbolos[var] = {'tipo': tipo, 'valor': None, 'lineas': [linea]}  # Guardar la línea de declaración
        elif nodo[0] == 'main':
            for decl in nodo[1]:  # Declaraciones dentro del main
                construir_tabla_simbolos(decl, tabla_simbolos, linea)

# Segunda pasada para evaluar expresiones y asignaciones, actualizando las líneas
def verificar_tipo(nodo, tabla_simbolos, linea=1):
    try:
        if isinstance(nodo, tuple):
            # Si el nodo es un programa
            if nodo[0] == 'main':
                declaraciones = []
                sentencias = []

                for decl in nodo[1]:
                    resultado_decl = verificar_tipo(decl, tabla_simbolos, linea)
                    declaraciones.append(resultado_decl)
                    if resultado_decl[0] == 'error':
                        declaraciones.append(('error', f"Error en la declaración {decl}"))

                for sent in nodo[2]:
                    resultado_sent = verificar_tipo(sent, tabla_simbolos, linea)
                    sentencias.append(resultado_sent)
                    if resultado_sent[0] == 'error':
                        sentencias.append(('error', f"Error en la sentencia {sent}"))

                return ('main', 'ok', declaraciones, sentencias)

            # Si es una declaración de variable
            if nodo[0] == 'decl':
                tipo = nodo[1]
                variables = []
                for var in nodo[2]:
                    if var.strip():  # Verificar que la variable no esté vacía
                        tabla_simbolos[var] = {'tipo': tipo, 'valor': None, 'lineas': [linea]}  # Añadir línea de declaración
                        variables.append(f"{var}.{tipo}.val(None)")  # Añadir el atributo var.tipo
                return ('decl', f"listvar.{tipo}", variables)

            # Si es una asignación
            elif nodo[0] == 'assign':
                var = nodo[1]
                exp = verificar_tipo(nodo[2], tabla_simbolos, linea)
                tipo_var = tabla_simbolos.get(var, None)
                if tipo_var is None:
                    return ('assign', 'error', f"Variable '{var}' no está declarada.", exp)
                
                # Comprobar que los tipos sean compatibles
                if len(exp) > 1 and tipo_var['tipo'] != exp[1].split('.')[0]:  # Comparamos solo el tipo (int o float)
                    return ('assign', 'error', f"Error de tipos: Se esperaba {tipo_var['tipo']} pero se encontró {exp[1]}", exp)
                
                # Asignar el valor y la línea de la asignación
                valor = obtener_valor(exp, tabla_simbolos)
                tabla_simbolos[var]['valor'] = valor  # Asignar el nuevo valor
                if linea not in tabla_simbolos[var]['lineas']:  # Asegurarse de que la línea esté registrada
                    tabla_simbolos[var]['lineas'].append(linea)
                return ('assign', f"{var}.{tipo_var['tipo']}", exp)

            # Si es una operación aritmética, procesar respetando la prioridad de operadores
            elif nodo[0] in ('+', '-', '*', '/'):
                tipo_izq = verificar_tipo(nodo[1], tabla_simbolos, linea)
                tipo_der = verificar_tipo(nodo[2], tabla_simbolos, linea)

                if tipo_izq[0] == 'error' or tipo_der[0] == 'error':
                    return ('error', f"Error en operandos de la operación {nodo[0]}")

                # Aplicar promoción de tipos (float si alguno es float, int si ambos son int)
                if 'float' in tipo_izq[1] or 'float' in tipo_der[1]:
                    tipo_final = 'float'
                else:
                    tipo_final = 'int'

                # Obtener los valores reales si son enteros o flotantes
                valor_izq = obtener_valor(tipo_izq, tabla_simbolos)
                valor_der = obtener_valor(tipo_der, tabla_simbolos)

                # Resolver la operación según el operador
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
                        resultado = valor_izq / valor_der

                    # Retorna el resultado junto con el tipo final de la operación
                    return ('numero', f"{tipo_final}", resultado)
                else:
                    return ('error', f"Error en la operación {nodo[0]}: tipos incompatibles {tipo_izq} y {tipo_der}")

            # Si es una operación de signo
            elif nodo[0] in ('+', '-'):
                signo = nodo[0]
                tipo_val = verificar_tipo(nodo[1], tabla_simbolos, linea)

                # Aplicar promoción de signos
                tipo_final = tipo_val[1]

                valor = obtener_valor(tipo_val, tabla_simbolos)
                if signo == '-':
                    valor = -valor

                return ('signo', f"{tipo_final}", valor)

            # Si es una condición if-else con bloques y delimitador fi
            elif nodo[0] == 'if_else':
                condicion = verificar_tipo(nodo[1], tabla_simbolos, linea)

                # Asegurarnos que la condición sea booleana
                if condicion[1] != 'bool':
                    return ('if_else', 'error', "Condición en 'if' debe ser booleana.", condicion)

                # Si la condición es True, procesar el bloque del 'then'
                bloque_then = verificar_bloque(nodo[2], tabla_simbolos, linea)
                if bloque_then[0] == 'error':
                    return ('if_else', 'error', f"Error en el bloque 'then': {bloque_then}")
                
                # Procesamos el bloque else (si existe)
                if len(nodo) > 3:
                    bloque_else = verificar_bloque(nodo[3], tabla_simbolos, linea)
                    if bloque_else[0] == 'error':
                        return ('if_else', 'error', f"Error en el bloque 'else': {bloque_else}")
                    return ('if_else', 'bool', bloque_then, bloque_else)
                
                return ('if_else', 'bool', bloque_then)

            # Si es un ciclo while
            elif nodo[0] == 'while':
                condicion = verificar_tipo(nodo[1], tabla_simbolos, linea)
                if condicion[1] != 'bool':
                    return ('while', 'error', "Condición en 'while' debe ser booleana.", condicion)
                
                # Procesar el cuerpo del "while" como un bloque
                cuerpo = verificar_bloque(nodo[2], tabla_simbolos, linea)
                return ('while', 'bool', cuerpo)

            # Si es un ciclo do-while
            elif nodo[0] == 'do_until':
                # Procesar el cuerpo del "do" como un bloque
                cuerpo = verificar_bloque(nodo[1], tabla_simbolos, linea)
                condicion = verificar_tipo(nodo[2], tabla_simbolos, linea)  # Verificar la condición del "until"
                if condicion[1] != 'bool':
                    return ('do_until', 'error', "Condición en 'do_until' debe ser booleana.", cuerpo, condicion)
                return ('do_until', 'bloque', cuerpo, condicion)

            # Si es una operación lógica
            elif nodo[0] in ('and', 'or'):
                tipo_izq = verificar_tipo(nodo[1], tabla_simbolos, linea)
                tipo_der = verificar_tipo(nodo[2], tabla_simbolos, linea)
                if tipo_izq[1] != 'bool' or tipo_der[1] != 'bool':
                    return (nodo[0], 'error', f"Error de tipos: Se esperaba 'bool' en una operación lógica.", tipo_izq, tipo_der)
                return (nodo[0], 'bool', tipo_izq, tipo_der)

            # Si es una operación de comparación
            elif nodo[0] in ('==', '!=', '<', '>', '<=', '>='):
                tipo_izq = verificar_tipo(nodo[1], tabla_simbolos, linea)
                tipo_der = verificar_tipo(nodo[2], tabla_simbolos, linea)
                if len(tipo_izq) > 1 and len(tipo_der) > 1 and tipo_izq[1] != tipo_der[1]:
                    return (nodo[0], 'error', f"Error de tipos: Comparación entre {tipo_izq[1]} y {tipo_der[1]}.", tipo_izq, tipo_der)
                return (nodo[0], 'bool', tipo_izq, tipo_der)

        # Si es un literal booleano (true o false)
        elif nodo in ('true', 'false'):
            return ('literal', 'bool', nodo)

        # Si es un número
        elif isinstance(nodo, (int, float)):
            tipo = 'int' if isinstance(nodo, int) else 'float'
            return ('numero', f"{tipo}", nodo)  # Incluye el tipo y el valor del número

        # Si es un identificador (variable)
        elif isinstance(nodo, str):
            tipo = tabla_simbolos.get(nodo, "undefined")
            if tipo == "undefined":
                return ('error', f"Variable '{nodo}' no está declarada.")
            # Registrar cada vez que se usa una variable en su lista de líneas
            if linea not in tabla_simbolos[nodo]['lineas']:
                tabla_simbolos[nodo]['lineas'].append(linea)
            return ('var', f"{tipo['tipo']}", f"{nodo}.{tipo['tipo']}.val")  # Concatenamos el nombre y el tipo con .val

        return ('error', f"Nodo no reconocido: {nodo}")

    except Exception as e:
        print(f"Error manejado: {e}")
        return ('error', f"Error en la operación: {str(e)}", nodo)

# Función para procesar bloques fragmentados
def verificar_bloque(bloque, tabla_simbolos, linea):
    # Asegurarnos de que estamos trabajando con una lista de sentencias
    if not isinstance(bloque, list):
        return ('error', "Bloque no reconocido o mal estructurado.")
    
    sentencias = []
    for sent in bloque:
        resultado_sent = verificar_tipo(sent, tabla_simbolos, linea)
        sentencias.append(resultado_sent)
        if resultado_sent[0] == 'error':
            sentencias.append(('error', f"Error en la sentencia {sent}"))
    
    if len(sentencias) == 0:
        return ('error', "Bloque vacío o no declarado.")
    return ('bloque', sentencias)

# Función para mostrar el árbol semántico sin detenerse ante errores
def analizar_semantico(arbol, tabla_simbolos):
    try:
        resultado = verificar_tipo(arbol, tabla_simbolos)
        return resultado
    except Exception as e:
        return ('error', str(e))

# Obtener valor de un nodo (ya sea variable o número)
def obtener_valor(nodo, tabla_simbolos):
    # Manejar números
    if nodo[0] == 'numero':
        return nodo[2]
    
    # Manejar variables
    elif nodo[0] == 'var':
        var_name = nodo[2].split('.')[0]
        tipo = tabla_simbolos.get(var_name, None)
        if tipo:
            return tipo['valor']  # Retorna el valor real si es un número o ya tiene valor
        else:
            raise ValueError(f"Variable '{var_name}' no está definida")
    
    # Manejar literales booleanos
    elif nodo[0] == 'literal' and nodo[1] == 'bool':
        # Retorna True o False según el literal
        if nodo[2] == 'true':
            return True
        elif nodo[2] == 'false':
            return False
        else:
            raise ValueError(f"Valor booleano inesperado: {nodo[2]}")
    
    # Si se encuentra un tipo de nodo inesperado
    else:
        raise ValueError(f"Tipo inesperado para nodo: {nodo}")
