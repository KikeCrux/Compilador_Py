# IDE
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import re
from analizador_lexico import analizar_lexico
from analizador_sintactico import analizar_sintactico
from analizador_semantico import analizar_semantico, construir_tabla_simbolos

class IDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador chafa")

        # Inicializar la tabla de símbolos como un diccionario vacío
        self.tabla_simbolos = {}

        frame_superior = tk.Frame(self.root)
        frame_superior.pack(side="top", fill="both", expand=True)

        self.lineas = tk.Text(frame_superior, width=4, padx=3, takefocus=0, border=0,
                              background='lightgrey', state='disabled', wrap='none')
        self.lineas.pack(side="left", fill="y")

        self.texto_scroll = tk.Scrollbar(frame_superior)
        self.texto_scroll.pack(side="right", fill="y")

        self.texto = tk.Text(frame_superior, wrap="none", yscrollcommand=self.sync_scroll, width=50, height=10)
        self.texto.pack(side="left", expand=True, fill="both")
        self.texto.bind("<KeyRelease>", self.on_key_release)

        self.texto_scroll.config(command=self.texto.yview)
        self.texto_scroll.config(command=self.sync_scroll)

        # Sincronizar scroll con números de línea
        self.texto_scroll.bind("<MouseWheel>", self.on_scroll)
        self.texto.bind("<MouseWheel>", self.on_scroll)

        self.pestanas = ttk.Notebook(frame_superior)
        self.pestanas.pack(side="right", expand=True, fill="both")

        # Pestaña para el análisis léxico
        self.panel_lexico = tk.Frame(self.pestanas)
        self.texto_lexico = scrolledtext.ScrolledText(self.panel_lexico, wrap="word", width=30, height=10)
        self.texto_lexico.pack(expand=True, fill="both")
        self.pestanas.add(self.panel_lexico, text="Lexico")

        # Pestaña para el análisis sintáctico
        self.panel_sintactico = tk.Frame(self.pestanas)
        self.texto_sintactico = ttk.Treeview(self.panel_sintactico)
        self.texto_sintactico.pack(expand=True, fill="both")
        self.pestanas.add(self.panel_sintactico, text="Sintactico")

        # Pestaña para el análisis semántico
        self.panel_semantico = tk.Frame(self.pestanas)
        self.texto_semantico = ttk.Treeview(self.panel_semantico)
        self.texto_semantico.pack(expand=True, fill="both")
        self.pestanas.add(self.panel_semantico, text="Semantico")

        # Pestaña para la tabla de símbolos
        self.panel_simbolos = tk.Frame(self.pestanas)
        self.texto_simbolos = scrolledtext.ScrolledText(self.panel_simbolos, wrap="word", width=30, height=10)
        self.texto_simbolos.pack(expand=True, fill="both")
        self.pestanas.add(self.panel_simbolos, text="Tabla de Símbolos")

        frame_inferior = tk.Frame(self.root)
        frame_inferior.pack(side="bottom", fill="both", expand=True)

        salida_compilador = tk.Label(frame_inferior, text="Salida de Compilación")
        salida_compilador.pack()

        self.salida_compilacion = tk.Text(frame_inferior, wrap="word", height=5)
        self.salida_compilacion.pack(expand=True, fill="both")

        resultado_error = tk.Label(frame_inferior, text="Resultado del Programa")
        resultado_error.pack()

        self.resultado_texto = tk.Text(frame_inferior, wrap="word", height=5)
        self.resultado_texto.pack(expand=True, fill="both")

        error_label = tk.Label(frame_inferior, text="Salida de Errores")
        error_label.pack()

        self.error_texto = tk.Text(frame_inferior, wrap="word", height=5)
        self.error_texto.pack(expand=True, fill="both")

        self.crear_menu()
        self.crear_botones_acceso_rapido()
        self.actualizar_numero_lineas()
        self.resaltar_sintaxis()

    def crear_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Abrir", command=self.abrir_archivo)
        archivo_menu.add_command(label="Guardar", command=self.guardar_archivo)
        archivo_menu.add_command(label="Guardar como...", command=self.guardar_como_archivo)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.root.destroy)

        compilar_menu = tk.Menu(menubar, tearoff=0)
        compilar_menu.add_command(label="Compilar", command=self.compilar_archivo)

        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        menubar.add_cascade(label="Compilar", menu=compilar_menu)

    def crear_botones_acceso_rapido(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack(side="top", fill="x")

        abrir_btn = tk.Button(toolbar, text="Abrir", command=self.abrir_archivo)
        abrir_btn.pack(side="left", padx=2, pady=2)

        guardar_btn = tk.Button(toolbar, text="Guardar", command=self.guardar_archivo)
        guardar_btn.pack(side="left", padx=2, pady=2)

        compilar_btn = tk.Button(toolbar, text="Compilar", command=self.compilar_archivo)
        compilar_btn.pack(side="left", padx=2, pady=2)

    def resaltar_sintaxis(self, event=None):
        self.texto.tag_remove("reservada", "1.0", tk.END)
        self.texto.tag_remove("string", "1.0", tk.END)
        self.texto.tag_remove("comentario", "1.0", tk.END)

        palabras_reservadas = [
            "bool", "int", "char", "byte", "long", "double", "if", "else",
            "while", "for", "switch", "case", "break", "try", "return",
            "void", "public", "protected", "private", "class", "abstract",
            "interface", "this", "friend", "do", "until", "float", "then", "fi",
            "and", "or"
        ]
        patron_palabras_reservadas = r'\b(?:' + '|'.join(palabras_reservadas) + r')\b'
        patron_string = r'\"([^\\\n]|(\\.))*?\"'
        patron_comentario = r'(//.*|/\*[\s\S]*?\*/)' 

        self.texto.tag_configure("reservada", foreground="blue")
        self.texto.tag_configure("string", foreground="red")
        self.texto.tag_configure("comentario", foreground="green")
        self.texto.tag_configure("error", background="yellow")

        texto = self.texto.get("1.0", tk.END)

        for match in re.finditer(patron_palabras_reservadas, texto):
            start, end = match.span()
            self.texto.tag_add("reservada", f"1.0+{start}c", f"1.0+{end}c")

        for match in re.finditer(patron_string, texto):
            start, end = match.span()
            self.texto.tag_add("string", f"1.0+{start}c", f"1.0+{end}c")

        for match in re.finditer(patron_comentario, texto):
            start, end = match.span()
            self.texto.tag_add("comentario", f"1.0+{start}c", f"1.0+{end}c")

    def abrir_archivo(self):
        archivo = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if archivo:
            with open(archivo, "r") as f:
                contenido = f.read()
                self.texto.delete("1.0", tk.END)
                self.texto.insert(tk.END, contenido)
                self.resaltar_sintaxis()
                self.actualizar_numero_lineas()

    def guardar_archivo(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if archivo:
            with open(archivo, "w") as f:
                f.write(self.texto.get("1.0", tk.END))

    def guardar_como_archivo(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if archivo:
            with open(archivo, "w") as f:
                f.write(self.texto.get("1.0", tk.END))

    def compilar_archivo(self):
        texto = self.texto.get("1.0", tk.END)
        self.mostrar_tokens_lexicos(texto)
        arbol_sintactico, errores_sintacticos = analizar_sintactico(texto)
        if errores_sintacticos:
            self.error_texto.delete("1.0", tk.END)
            for error in errores_sintacticos:
                self.error_texto.insert(tk.END, error + "\n")
            return
        
        self.mostrar_arbol_sintactico(texto)
        
        # Crear tabla de símbolos preliminar
        self.tabla_simbolos = {}
        construir_tabla_simbolos(arbol_sintactico, self.tabla_simbolos)
        
        # Pasar la tabla de símbolos al análisis semántico
        resultado_semantico = analizar_semantico(arbol_sintactico, self.tabla_simbolos)
        
        # Mostrar la tabla de símbolos
        self.mostrar_tabla_simbolos()

        # Mostrar resultados del análisis semántico
        self.mostrar_arbol_semantico(texto)

    def mostrar_tokens_lexicos(self, texto):
        self.texto_lexico.delete("1.0", tk.END)
        tokens = analizar_lexico(texto)
        self.texto_lexico.insert(tk.END, f"{'Clave':<12} {'Lexema':<12} {'Fila':<5} {'Columna':<10}\n")
        self.texto_lexico.insert(tk.END, f"{'-'*45}\n")
        for token in tokens:
            lexema = str(token.value)
            fila = token.lineno
            columna = "N/A"
            if hasattr(token, 'column'):
                columna = token.column
            # No se incluye la columna, ya que no es necesaria
            self.texto_lexico.insert(tk.END, f"{token.type:<12} {lexema:<12} {fila:<5} {columna:<5}\n")

    def mostrar_arbol_sintactico(self, texto):
        self.error_texto.delete("1.0", tk.END)
        self.limpiar_arbol_sintactico()
        self.texto.tag_remove("error", "1.0", tk.END)
        try:
            resultado, errores = analizar_sintactico(texto)
            if resultado:
                self.insertar_arbol_sintactico(resultado)
            if errores:
                for error in errores:
                    self.error_texto.insert(tk.END, error + "\n")
                    match = re.search(r'línea (\d+)', error)
                    if match:
                        linea_error = int(match.group(1))
                        self.texto.tag_add("error", f"{linea_error}.0", f"{linea_error}.end")
        except SyntaxError as e:
            self.error_texto.insert(tk.END, str(e))

    def mostrar_tabla_simbolos(self):
        self.texto_simbolos.delete("1.0", tk.END)
        for var, info in self.tabla_simbolos.items():
            self.texto_simbolos.insert(tk.END, f"Variable: {var} | Tipo: {info['tipo']} | Línea(s): {info['lineas']}\n")

    def mostrar_arbol_semantico(self, texto):
        self.limpiar_arbol_semantico()
        resultado, _ = analizar_sintactico(texto)
        if resultado:
            resultado_semantico = analizar_semantico(resultado, self.tabla_simbolos)
            if resultado_semantico and resultado_semantico[0] != 'error':
                self.insertar_arbol_semantico("", resultado_semantico)
            else:
                self.texto_semantico.insert("", "end", text=f"Error en el análisis semántico: {resultado_semantico[1]}")
        else:
            self.texto_semantico.insert("", "end", text="No se pudo generar un árbol semántico.")

    def limpiar_arbol_semantico(self):
        for item in self.texto_semantico.get_children():
            self.texto_semantico.delete(item)

    def insertar_arbol_semantico(self, parent, nodo):
        if isinstance(nodo, tuple):
            item = self.texto_semantico.insert(parent, "end", text=f"{nodo[0]}: {nodo[1]}", open=True)
            for subnodo in nodo[2:]:
                self.insertar_arbol_semantico(item, subnodo)
        elif isinstance(nodo, list):
            for subnodo in nodo:
                self.insertar_arbol_semantico(parent, subnodo)
        else:
            self.texto_semantico.insert(parent, "end", text=str(nodo))

    def limpiar_arbol_sintactico(self):
        for item in self.texto_sintactico.get_children():
            self.texto_sintactico.delete(item)

    def insertar_arbol_sintactico(self, arbol):
        self.insertar_nodo("", arbol)

    def insertar_nodo(self, parent, nodo):
        if isinstance(nodo, tuple):
            if nodo[0] == 'decl':
                item = self.texto_sintactico.insert(parent, "end", text=f"{nodo[0]}")
                tipo_item = self.texto_sintactico.insert(item, "end", text=f"{nodo[1]} {' '.join(nodo[2])}")
                self.texto_sintactico.item(tipo_item, open=True)
                self.texto_sintactico.item(item, open=True)
            elif nodo[0] == 'assign':
                item = self.texto_sintactico.insert(parent, "end", text=f"{nodo[0]}")
                variable_item = self.texto_sintactico.insert(item, "end", text=f"{nodo[1]} = {nodo[2]}")
                self.texto_sintactico.item(variable_item, open=True)
                self.texto_sintactico.item(item, open=True)
                self.insertar_nodo(item, nodo[2])
            else:
                item = self.texto_sintactico.insert(parent, "end", text=str(nodo[0]), open=True)
                for subnodo in nodo[1:]:
                    self.insertar_nodo(item, subnodo)
                self.texto_sintactico.item(item, open=True)
        elif isinstance(nodo, list):
            for subnodo in nodo:
                self.insertar_nodo(parent, subnodo)
        else:
            item = self.texto_sintactico.insert(parent, "end", text=str(nodo))
            self.texto_sintactico.item(item, open=True)

    def actualizar_numero_lineas(self, event=None):
        self.lineas.config(state='normal')
        self.lineas.delete('1.0', 'end')

        num_lineas = int(self.texto.index('end-1c').split('.')[0])
        for i in range(1, num_lineas + 1):
            self.lineas.insert(tk.END, f'{i}\n')

        self.lineas.config(state='disabled')

    def sync_scroll(self, *args):
        self.lineas.yview_moveto(args[0])
        self.texto.yview_moveto(args[0])

    def on_scroll(self, event):
        self.texto.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.lineas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def on_key_release(self, event):
        self.actualizar_numero_lineas()
        self.resaltar_sintaxis()

if __name__ == "__main__":
    root = tk.Tk()
    editor = IDE(root)
    root.mainloop()
