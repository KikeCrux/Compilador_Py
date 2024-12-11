# code_generator.py

class CodeGenerator:
    def __init__(self):
        self.instructions = []
        self.symtab = {}  
        self.next_address = 0 
        self.label_counter = 0 
        self.inst_counter = 0  
        self.labels = {}  

    def new_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def generate_code(self, node):
        # Genera código para el nodo del AST
        # Retorna la dirección de instrucción si es necesario
        method_name = f"gen_{node[0]}"
        method = getattr(self, method_name, self.gen_default)
        return method(node)

    def gen_default(self, node):
        # Método por defecto para generación de código
        print(f"No hay método de generación para el nodo tipo {node[0]}")
        return None

    def gen_main(self, node):
        # ('main', lista_decl, lista_sent, lineno)
        decls = node[1]
        stmts = node[2]
        # Generar código para declaraciones
        for decl in decls:
            self.generate_code(decl)
        # Generar código para sentencias
        for stmt in stmts:
            self.generate_code(stmt)
        # Agregar instrucción HALT al final
        self.instructions.append(f"{self.inst_counter}: HALT 0,0,0")
        self.inst_counter += 1

    def gen_decl(self, node):
        # ('decl', tipo, variables, lineno)
        tipo = node[1]
        variables = node[2]
        for var in variables:
            if var not in self.symtab:
                self.symtab[var] = self.next_address
                self.next_address += 1
            else:
                print(f"Variable {var} ya declarada")
        # Las declaraciones no generan código

    def gen_assign(self, node):
        # ('assign', var, exp, lineno)
        var = node[1]
        exp = node[2]
        if var not in self.symtab:
            print(f"Variable {var} no declarada, asignando dirección {self.next_address}")
            self.symtab[var] = self.next_address
            self.next_address += 1
        # Generar código para la expresión y almacenar resultado en un registro
        # Usamos el registro 0 para simplicidad
        self.generate_expression(exp, 0)
        # Almacenar el resultado del registro 0 en la dirección de la variable
        addr = self.symtab[var]
        self.instructions.append(f"{self.inst_counter}: ST 0,{addr}(0)")
        self.inst_counter += 1

    def generate_expression(self, exp, reg):
        # Genera código para la expresión y almacena el resultado en reg
        if isinstance(exp, tuple):
            if len(exp) >= 2 and isinstance(exp[-1], int):
                # Remover el número de línea
                exp = exp[:-1]

            if len(exp) == 4:
                op = exp[0]
                left = exp[1]
                right = exp[2]
                lineno = exp[3]
            else:
                op = exp[0]
                left = exp[1]
                right = exp[2]
                lineno = None

            # Generar código para el operando izquierdo en reg
            self.generate_expression(left, reg)
            # Generar código para el operando derecho en reg+1
            self.generate_expression(right, reg + 1)
            op_map = {
                '+': 'ADD',
                '-': 'SUB',
                '*': 'MUL',
                '/': 'DIV',
                '<': 'LES',
                '>': 'GE',
                '<=': 'LEQ',
                '>=': 'GEQ',
                '==': 'EQU',
                '!=': 'NEQ',
                'and': 'AND',
                'or': 'OR',
            }
            if op in op_map:
                inst = op_map[op]
                self.instructions.append(f"{self.inst_counter}: {inst} {reg},{reg},{reg+1}")
                self.inst_counter += 1
            else:
                print(f"Operador no soportado {op}")
        elif isinstance(exp, tuple) and len(exp) == 3:
            # Operador unario
            op = exp[0]
            operand = exp[1]
            lineno = exp[2]
            self.generate_expression(operand, reg)
            op_map = {
                '!': 'NEG',
                '-': 'MIN',
            }
            if op in op_map:
                inst = op_map[op]
                self.instructions.append(f"{self.inst_counter}: {inst} {reg},{reg},0")
                self.inst_counter += 1
            else:
                print(f"Operador unario no soportado {op}")
        elif isinstance(exp, str):
            # Variable o constante
            if exp.lower() in ('true', 'false'):
                # Booleanos
                val = 1 if exp.lower() == 'true' else 0
                self.instructions.append(f"{self.inst_counter}: LDC {reg},{val}(0)")
                self.inst_counter += 1
            elif exp in self.symtab:
                addr = self.symtab[exp]
                self.instructions.append(f"{self.inst_counter}: LD {reg},{addr}(0)")
                self.inst_counter += 1
            else:
                print(f"Variable {exp} no declarada, asignando dirección {self.next_address}")
                self.symtab[exp] = self.next_address
                self.next_address += 1
                addr = self.symtab[exp]
                self.instructions.append(f"{self.inst_counter}: LD {reg},{addr}(0)")
                self.inst_counter += 1
        elif isinstance(exp, int):
            self.instructions.append(f"{self.inst_counter}: LDC {reg},{exp}(0)")
            self.inst_counter += 1
        elif isinstance(exp, float):
            # Modificación necesaria para utilizar LDF con flotantes
            self.instructions.append(f"{self.inst_counter}: LDF {reg},{exp}(0)")
            self.inst_counter += 1
        else:
            print(f"Expresión no soportada {exp}")

    def gen_bloque(self, node):
        # ('bloque', lista_sentencias, lineno)
        statements = node[1]
        for stmt in statements:
            self.generate_code(stmt)

    def gen_if(self, node):
        # ('if', condition, then_block, lineno)
        condition = node[1]
        then_block = node[2]
        endif_label = self.new_label()
        # Generar código para la condición en el registro 0
        self.generate_expression(condition, 0)
        # Si la condición es falsa, saltar a endif_label
        self.instructions.append(f"{self.inst_counter}: JEQ 0,{endif_label}(0)")
        self.inst_counter += 1
        # Generar código para el bloque 'then'
        self.generate_code(then_block)
        # Etiqueta endif_label
        self.labels[endif_label] = self.inst_counter

    def gen_if_else(self, node):
        # ('if_else', condition, then_block, else_block, lineno)
        condition = node[1]
        then_block = node[2]
        else_block = node[3]
        else_label = self.new_label()
        endif_label = self.new_label()
        # Generar código para la condición
        self.generate_expression(condition, 0)
        # Si la condición es falsa, saltar a else_label
        self.instructions.append(f"{self.inst_counter}: JEQ 0,{else_label}(0)")
        self.inst_counter += 1
        # Generar código para el bloque 'then'
        self.generate_code(then_block)
        # Saltar a endif_label
        self.instructions.append(f"{self.inst_counter}: LDA 7,{endif_label}(0)")
        self.inst_counter += 1
        # Etiqueta else_label
        self.labels[else_label] = self.inst_counter
        # Generar código para el bloque 'else'
        self.generate_code(else_block)
        # Etiqueta endif_label
        self.labels[endif_label] = self.inst_counter

    def gen_while(self, node):
        # ('while', condition, body_block, lineno)
        condition = node[1]
        body_block = node[2]
        start_label = self.new_label()
        end_label = self.new_label()
        # Etiqueta start_label
        self.labels[start_label] = self.inst_counter
        # Generar código para la condición
        self.generate_expression(condition, 0)
        # Si la condición es falsa, saltar a end_label
        self.instructions.append(f"{self.inst_counter}: JEQ 0,{end_label}(0)")
        self.inst_counter += 1
        # Generar código para el cuerpo del bucle
        self.generate_code(body_block)
        # Saltar al inicio del bucle
        self.instructions.append(f"{self.inst_counter}: LDA 7,{self.labels[start_label]}(0)")
        self.inst_counter += 1
        # Etiqueta end_label
        self.labels[end_label] = self.inst_counter

    def gen_do_until(self, node):
        # ('do_until', body_block, condition, lineno)
        body_block = node[1]
        condition = node[2]
        start_label = self.inst_counter
        # Generar código para el cuerpo del bucle
        self.generate_code(body_block)
        # Generar código para la condición
        self.generate_expression(condition, 0)
        # Si la condición es falsa, saltar al inicio del bucle
        self.instructions.append(f"{self.inst_counter}: JEQ 0,{start_label}(0)")
        self.inst_counter += 1

    def gen_read(self, node):
        # ('read', var_name, lineno)
        var_name = node[1]
        if var_name not in self.symtab:
            print(f"Variable {var_name} no declarada, asignando dirección {self.next_address}")
            self.symtab[var_name] = self.next_address
            self.next_address += 1
        addr = self.symtab[var_name]
        # Leer en el registro 0
        self.instructions.append(f"{self.inst_counter}: IN 0,0,0")
        self.inst_counter += 1
        # Almacenar el registro 0 en la dirección de la variable
        self.instructions.append(f"{self.inst_counter}: ST 0,{addr}(0)")
        self.inst_counter += 1

    def gen_write(self, node):
        # ('write', exp, lineno)
        exp = node[1]
        # Generar código para la expresión en el registro 0
        self.generate_expression(exp, 0)
        # Salida desde el registro 0
        self.instructions.append(f"{self.inst_counter}: OUT 0,0,0")
        self.inst_counter += 1

    def gen_break(self, node):
        # Manejar sentencias 'break'
        print("Sentencias 'break' no implementadas en el generador de código")

    def resolve_labels(self):
        # Reemplazar etiquetas por direcciones de instrucción
        label_addresses = {}
        for label, addr in self.labels.items():
            label_addresses[label] = addr
        resolved_instructions = []
        for inst in self.instructions:
            # Reemplazar etiquetas en las instrucciones
            for label, addr in label_addresses.items():
                inst = inst.replace(f"{label}", str(addr))
            resolved_instructions.append(inst)
        self.instructions = resolved_instructions

    def write_code(self, filename=None):
        self.resolve_labels()
        code_output = '\n'.join(self.instructions)
        if filename:
            with open(filename, 'w') as f:
                f.write(code_output)
        return code_output