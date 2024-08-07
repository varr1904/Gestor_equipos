import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
from PIL import Image, ImageTk
import io

class DispositivoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrador de Dispositivos")
        self.root.geometry("800x600")

        self.conn = sqlite3.connect('dispositivos.db')
        self.crear_tabla()

        self.crear_widgets()
        self.cargar_dispositivos()

        # Hacer que la ventana sea responsive
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def crear_tabla(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dispositivos (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                ubicacion TEXT,
                estado TEXT,
                foto BLOB
            )
        ''')
        self.conn.commit()

    def crear_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)

        # Frame de entrada de datos
        input_frame = ttk.LabelFrame(main_frame, text="Datos del Dispositivo", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        input_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="ID:").grid(row=0, column=0, sticky=tk.W)
        self.id_entry = ttk.Entry(input_frame)
        self.id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(input_frame, text="Nombre:").grid(row=1, column=0, sticky=tk.W)
        self.nombre_entry = ttk.Entry(input_frame)
        self.nombre_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        ttk.Label(input_frame, text="Ubicación:").grid(row=2, column=0, sticky=tk.W)
        self.ubicacion_entry = ttk.Entry(input_frame)
        self.ubicacion_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        ttk.Label(input_frame, text="Estado:").grid(row=3, column=0, sticky=tk.W)
        self.estado_entry = ttk.Entry(input_frame)
        self.estado_entry.grid(row=3, column=1, sticky=(tk.W, tk.E))

        self.foto_button = ttk.Button(input_frame, text="Seleccionar Foto", command=self.seleccionar_foto)
        self.foto_button.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        self.guardar_button = ttk.Button(input_frame, text="Guardar", command=self.guardar_dispositivo)
        self.guardar_button.grid(row=5, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        # Frame de filtro de búsqueda
        filter_frame = ttk.LabelFrame(main_frame, text="Filtro de Búsqueda", padding="10")
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        filter_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(filter_frame, text="Buscar:").grid(row=0, column=0, sticky=tk.W)
        self.search_entry = ttk.Entry(filter_frame)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        self.search_by = ttk.Combobox(filter_frame, values=["ID", "Nombre", "Ubicación", "Estado"])
        self.search_by.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=5)
        self.search_by.set("Nombre")  # Valor por defecto
        
        ttk.Button(filter_frame, text="Buscar", command=self.filtrar_dispositivos).grid(row=0, column=3, padx=5)
        ttk.Button(filter_frame, text="Limpiar", command=self.limpiar_filtro).grid(row=0, column=4, padx=5)

        # Frame de visualización de datos
        data_frame = ttk.Frame(main_frame)
        data_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        data_frame.grid_columnconfigure(0, weight=1)
        data_frame.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(data_frame, columns=("ID", "Nombre", "Ubicación", "Estado"), show="headings")
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Ubicación", text="Ubicación")
        self.tree.heading("Estado", text="Estado")

        # Scrollbar para el Treeview
        scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Frame para la imagen
        self.imagen_frame = ttk.LabelFrame(main_frame, text="Foto del Dispositivo", padding="10")
        self.imagen_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        self.imagen_frame.grid_columnconfigure(0, weight=1)
        self.imagen_frame.grid_rowconfigure(0, weight=1)

        self.imagen_label = ttk.Label(self.imagen_frame)
        self.imagen_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="Editar", command=self.editar_dispositivo).grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_dispositivo).grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))

    def seleccionar_foto(self):
        self.ruta_foto = filedialog.askopenfilename(filetypes=[("Imagen", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if self.ruta_foto:
            self.mostrar_imagen(self.ruta_foto)

    def mostrar_imagen(self, ruta):
        imagen = Image.open(ruta)
        imagen = imagen.resize((200, 200), Image.LANCZOS)
        foto = ImageTk.PhotoImage(imagen)
        self.imagen_label.config(image=foto)
        self.imagen_label.image = foto

    def guardar_dispositivo(self):
        id = self.id_entry.get()
        nombre = self.nombre_entry.get()
        ubicacion = self.ubicacion_entry.get()
        estado = self.estado_entry.get()

        if not all([id, nombre, ubicacion, estado]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            with open(self.ruta_foto, "rb") as file:
                foto_blob = file.read()
        except AttributeError:
            messagebox.showerror("Error", "Debe seleccionar una foto")
            return

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO dispositivos (id, nombre, ubicacion, estado, foto)
            VALUES (?, ?, ?, ?, ?)
        ''', (id, nombre, ubicacion, estado, foto_blob))
        self.conn.commit()

        self.cargar_dispositivos()
        self.limpiar_campos()

    def cargar_dispositivos(self):
        self.tree.delete(*self.tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nombre, ubicacion, estado FROM dispositivos")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        self.tree.bind("<<TreeviewSelect>>", self.mostrar_foto_seleccionada)

    def mostrar_foto_seleccionada(self, event):
        seleccion = self.tree.selection()
        if seleccion:
            item = self.tree.item(seleccion[0])
            id = item['values'][0]
            cursor = self.conn.cursor()
            cursor.execute("SELECT foto FROM dispositivos WHERE id = ?", (id,))
            foto_blob = cursor.fetchone()[0]
            
            imagen = Image.open(io.BytesIO(foto_blob))
            imagen = imagen.resize((200, 200), Image.LANCZOS)
            foto = ImageTk.PhotoImage(imagen)
            self.imagen_label.config(image=foto)
            self.imagen_label.image = foto

    def editar_dispositivo(self):
        seleccion = self.tree.selection()
        if seleccion:
            item = self.tree.item(seleccion[0])
            valores = item['values']
            self.id_entry.delete(0, tk.END)
            self.id_entry.insert(0, valores[0])
            self.nombre_entry.delete(0, tk.END)
            self.nombre_entry.insert(0, valores[1])
            self.ubicacion_entry.delete(0, tk.END)
            self.ubicacion_entry.insert(0, valores[2])
            self.estado_entry.delete(0, tk.END)
            self.estado_entry.insert(0, valores[3])
            self.mostrar_foto_seleccionada(None)

    def eliminar_dispositivo(self):
        seleccion = self.tree.selection()
        if seleccion:
            item = self.tree.item(seleccion[0])
            id = item['values'][0]
            confirmacion = messagebox.askyesno("Confirmar eliminación", "¿Está seguro de que desea eliminar este dispositivo?")
            if confirmacion:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM dispositivos WHERE id = ?", (id,))
                self.conn.commit()
                self.cargar_dispositivos()
                self.limpiar_campos()

    def limpiar_campos(self):
        self.id_entry.delete(0, tk.END)
        self.nombre_entry.delete(0, tk.END)
        self.ubicacion_entry.delete(0, tk.END)
        self.estado_entry.delete(0, tk.END)
        self.imagen_label.config(image="")

    def filtrar_dispositivos(self):
        busqueda = self.search_entry.get()
        criterio = self.search_by.get().lower()
        
        self.tree.delete(*self.tree.get_children())
        cursor = self.conn.cursor()
        
        query = f"SELECT id, nombre, ubicacion, estado FROM dispositivos WHERE {criterio} LIKE ?"
        cursor.execute(query, (f"%{busqueda}%",))
        
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def limpiar_filtro(self):
        self.search_entry.delete(0, tk.END)
        self.cargar_dispositivos()

if __name__ == "__main__":
    root = tk.Tk()
    app = DispositivoApp(root)
    root.mainloop()