import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random
import time
import threading

class Proceso:
    def __init__(self, pid, prioridad, tiempo, color):
        self.pid = pid
        self.prioridad = prioridad
        self.tiempo = tiempo
        self.color = color
        self.estado = "Nuevo"
        self.canvas_obj = None
        self.pc = random.randint(1000, 2000)
        self.memoria_total = random.randint(256, 1024)
        self.codigo = random.randint(100, 400)
        self.datos = random.randint(50, 200)
        self.heap = random.randint(50, 200)
        self.stack = self.memoria_total - self.codigo - self.datos - self.heap

    def __str__(self):
        return f"PID: {self.pid}, Prioridad: {self.prioridad}, Tiempo: {self.tiempo}, Estado: {self.estado}"

class SimuladorSO(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Estados de Procesos")
        self.geometry("1000x800")
        self.configure(bg="#f0f0f0")

        self.procesos = []
        self.proceso_en_ejecucion = None

        self.setup_ui()

    def setup_ui(self):
        # Crear un frame principal
        main_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(main_frame, text="Simulador de Estados de Procesos", font=("Arial", 18, "bold"), bg="#f0f0f0")
        titulo.pack(pady=10)

        # Canvas para el diagrama de estados
        self.canvas = tk.Canvas(main_frame, width=900, height=400, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(pady=10)

        self.dibujar_estados()

        # Frame para los botones
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(pady=10)

        # Botones estilizados
        self.boton_agregar = tk.Button(button_frame, text="Agregar Proceso", command=self.agregar_proceso,
                                       bg="#4CAF50", fg="white", font=("Arial", 12), padx=10, pady=5)
        self.boton_agregar.pack(side=tk.LEFT, padx=5)

        self.boton_iniciar = tk.Button(button_frame, text="Iniciar Simulación", command=self.iniciar_simulacion,
                                       bg="#008CBA", fg="white", font=("Arial", 12), padx=10, pady=5)
        self.boton_iniciar.pack(side=tk.LEFT, padx=5)

        # Label para mostrar el estado actual
        self.label_estado = tk.Label(main_frame, text="", font=("Arial", 12), fg="#333333", bg="#f0f0f0")
        self.label_estado.pack(pady=10)

        # Tabla de procesos
        self.setup_tabla(main_frame)

    def setup_tabla(self, parent):
        # Estilo para la tabla
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#D3D3D3", fieldbackground="#D3D3D3", foreground="black")
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))

        columns = ("PID", "Estado", "Prioridad", "PC", "Memoria Total", "Código", "Datos", "Heap", "Stack")
        self.tabla = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100, anchor="center")

        self.tabla.pack(pady=10, fill=tk.BOTH, expand=True)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def dibujar_estados(self):
        self.estados = {
            "Nuevo": (100, 100),
            "Listo": (300, 100),
            "En Ejecución": (500, 100),
            "Bloqueado": (400, 300),
            "Terminado": (700, 100)
        }

        for estado, coords in self.estados.items():
            x, y = coords
            self.canvas.create_oval(x - 60, y - 30, x + 60, y + 30, fill="#E1F5FE", outline="#01579B", width=2)
            self.canvas.create_text(x, y, text=estado, font=("Arial", 12, "bold"), fill="#01579B")

        # Dibujar las transiciones
        self.dibujar_transicion(self.estados["Nuevo"], self.estados["Listo"], "Admitir")
        self.dibujar_transicion(self.estados["Listo"], self.estados["En Ejecución"], "Despachar")
        self.dibujar_transicion(self.estados["En Ejecución"], self.estados["Terminado"], "Salir")
        self.dibujar_transicion(self.estados["En Ejecución"], self.estados["Bloqueado"], "Esperar", curve=30)
        self.dibujar_transicion(self.estados["Bloqueado"], self.estados["Listo"], "Despertar", curve=-30)
        self.dibujar_transicion(self.estados["En Ejecución"], self.estados["Listo"], "Interrumpir", curve=-30)

    def dibujar_transicion(self, start, end, label, curve=0):
        x1, y1 = start
        x2, y2 = end
        if curve:
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2 - curve
            self.canvas.create_line(x1, y1, cx, cy, x2, y2, smooth=True, arrow=tk.LAST, fill="#757575")
            self.canvas.create_text(cx, cy - 15, text=label, font=("Arial", 10), fill="#757575")
        else:
            self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill="#757575")
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2 - 15, text=label, font=("Arial", 10), fill="#757575")

    def agregar_proceso(self):
        pid = len(self.procesos) + 1
        prioridad = random.randint(1, 10)
        tiempo = random.randint(5, 20)
        color = random.choice(["#FF5722", "#4CAF50", "#2196F3", "#FFC107", "#9C27B0", "#FF9800"])
        proceso = Proceso(pid, prioridad, tiempo, color)
        self.procesos.append(proceso)

        x, y = self.estados["Nuevo"]
        proceso.canvas_obj = self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill=proceso.color)

        self.tabla.insert("", "end", values=(proceso.pid, proceso.estado, proceso.prioridad, proceso.pc, 
                                             f"{proceso.memoria_total} KB", f"{proceso.codigo} KB", 
                                             f"{proceso.datos} KB", f"{proceso.heap} KB", f"{proceso.stack} KB"))

        messagebox.showinfo("Proceso agregado", f"Proceso {proceso.pid} agregado a 'Nuevo'")

    def actualizar_estado(self, proceso, nuevo_estado):
        proceso.estado = nuevo_estado
        x, y = self.estados[nuevo_estado]
        self.canvas.coords(proceso.canvas_obj, x - 15, y - 15, x + 15, y + 15)

        for item in self.tabla.get_children():
            if self.tabla.item(item)["values"][0] == proceso.pid:
                self.tabla.item(item, values=(proceso.pid, proceso.estado, proceso.prioridad, proceso.pc, 
                                              f"{proceso.memoria_total} KB", f"{proceso.codigo} KB", 
                                              f"{proceso.datos} KB", f"{proceso.heap} KB", f"{proceso.stack} KB"))
                break

        self.label_estado.config(text=f"Proceso {proceso.pid} está en {nuevo_estado}")

    def iniciar_simulacion(self):
        if not self.procesos:
            messagebox.showwarning("Advertencia", "No hay procesos para simular.")
            return

        self.boton_iniciar.config(state=tk.DISABLED)
        threading.Thread(target=self.simular, daemon=True).start()

    def simular(self):
        while self.procesos:
            self.procesos.sort(key=lambda p: p.prioridad)
            proceso = self.procesos.pop(0)
            self.actualizar_estado(proceso, "Listo")
            time.sleep(1)

            self.actualizar_estado(proceso, "En Ejecución")
            for _ in range(proceso.tiempo):
                time.sleep(0.5)
                proceso.pc += random.randint(1, 10)
                self.actualizar_estado(proceso, "En Ejecución")

            if random.choice([True, False]):
                self.actualizar_estado(proceso, "Bloqueado")
                time.sleep(1)
                self.actualizar_estado(proceso, "Listo")
                self.procesos.append(proceso)
            else:
                self.actualizar_estado(proceso, "Terminado")
                time.sleep(1)
                for item in self.tabla.get_children():
                    if self.tabla.item(item)["values"][0] == proceso.pid:
                        self.tabla.delete(item)
                        break
                self.canvas.delete(proceso.canvas_obj)

        self.label_estado.config(text="Simulación Terminada")
        self.boton_iniciar.config(state=tk.NORMAL)

if __name__ == "__main__":
    simulador = SimuladorSO()
    simulador.mainloop()