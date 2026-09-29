# La interfaz esta echa con IA por practicidad y facilidad
import tkinter as tk
from tkinter import ttk, messagebox
from functools import reduce
from typing import List, Dict, Callable

CATEGORIAS = ["Electricidad", "Combustible", "Gas Natural"]
REGIONES = ["Norte", "Centro", "Sur"]

REGISTROS_AMBIENTALES: List[Dict] = [
    {"id": "REG-01", "fuente": "Planta Ensambladora A", "categoria": "Electricidad", "consumo": 12500.0, "factor": 0.45, "region": "Norte", "activo": True},
    {"id": "REG-02", "fuente": "Flotilla Reparto 1", "categoria": "Combustible", "consumo": 3400.0, "factor": 2.31, "region": "Centro", "activo": True},
    {"id": "REG-03", "fuente": "Oficinas Centrales", "categoria": "Electricidad", "consumo": 4500.0, "factor": 0.45, "region": "Centro", "activo": True},
    {"id": "REG-04", "fuente": "Calderas Industriales", "categoria": "Gas Natural", "consumo": 8900.0, "factor": 1.98, "region": "Norte", "activo": False},
    {"id": "REG-05", "fuente": "Planta Ensambladora B", "categoria": "Electricidad", "consumo": 18200.0, "factor": 0.50, "region": "Sur", "activo": True},
    {"id": "REG-06", "fuente": "Flotilla Reparto 2", "categoria": "Combustible", "consumo": 1200.0, "factor": 2.31, "region": "Sur", "activo": True},
    {"id": "REG-07", "fuente": "Almacén Refrigerado", "categoria": "Electricidad", "consumo": 6700.0, "factor": 0.45, "region": "Norte", "activo": True},
]


def calcular_co2(registro: Dict) -> Dict:
    return {**registro, "co2_toneladas": round((registro["consumo"] * registro["factor"]) / 1000, 3)}


def crear_filtro_categoria(categoria: str) -> Callable[[Dict], bool]:
    return lambda r: categoria.lower() == "todas" or r["categoria"].lower() == categoria.lower()


def calcular_promedio_recursivo(lista: List[float], acumulado: float = 0.0, contador: int = 0) -> float:
    if not lista:
        return acumulado / contador if contador > 0 else 0.0
    return calcular_promedio_recursivo(lista[1:], acumulado + lista[0], contador + 1)


def crear_registro(registros: List[Dict], fuente: str, categoria: str, consumo: float,
                factor: float, region: str, activo: bool) -> Dict:
    return {
        "id": f"REG-{len(registros) + 1:02d}",
        "fuente": fuente,
        "categoria": categoria,
        "consumo": consumo,
        "factor": factor,
        "region": region,
        "activo": activo,
    }


def agregar_registro(registros: List[Dict], nuevo: Dict) -> List[Dict]:
    return registros + [nuevo]


def pipeline_eco_analyzer(datos: List[Dict], categoria_filtro: str, umbral_min_co2: float):
    registros_activos = (r for r in datos if r["activo"])
    registros_con_co2 = map(calcular_co2, registros_activos)
    filtro_cat = crear_filtro_categoria(categoria_filtro)
    registros_filtrados = filter(
        lambda r: filtro_cat(r) and r["co2_toneladas"] >= umbral_min_co2,
        registros_con_co2
    )
    resultados = list(registros_filtrados)
    total_co2 = reduce(lambda acc, r: acc + r["co2_toneladas"], resultados, 0.0)
    lista_co2 = [r["co2_toneladas"] for r in resultados]
    promedio_co2 = calcular_promedio_recursivo(lista_co2)
    return resultados, total_co2, promedio_co2


class DialogoAgregar(tk.Toplevel):
    def __init__(self, parent, al_guardar: Callable[[str, str, float, float, str, bool], None]):
        super().__init__(parent)
        self.al_guardar = al_guardar
        self.title("Agregar Registro")
        self.config(bg="#eef2f5", padx=20, pady=15)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        etiquetas = ["Fuente de emisión:", "Categoría:", "Consumo:", "Factor de emisión:", "Región:"]
        for i, texto in enumerate(etiquetas):
            tk.Label(self, text=texto, bg="#eef2f5").grid(row=i, column=0, sticky="e", padx=5, pady=6)

        self.entry_fuente = ttk.Entry(self, width=28)
        self.entry_fuente.grid(row=0, column=1, padx=5, pady=6)

        self.combo_cat = ttk.Combobox(self, values=CATEGORIAS, state="readonly", width=25)
        self.combo_cat.current(0)
        self.combo_cat.grid(row=1, column=1, padx=5, pady=6)

        self.entry_consumo = ttk.Entry(self, width=28)
        self.entry_consumo.grid(row=2, column=1, padx=5, pady=6)

        self.entry_factor = ttk.Entry(self, width=28)
        self.entry_factor.grid(row=3, column=1, padx=5, pady=6)

        self.combo_region = ttk.Combobox(self, values=REGIONES, state="readonly", width=25)
        self.combo_region.current(0)
        self.combo_region.grid(row=4, column=1, padx=5, pady=6)

        self.var_activo = tk.BooleanVar(value=True)
        tk.Checkbutton(self, text="Registro activo", variable=self.var_activo, bg="#eef2f5").grid(
            row=5, column=1, sticky="w", padx=5, pady=6
        )

        frame_botones = tk.Frame(self, bg="#eef2f5")
        frame_botones.grid(row=6, column=0, columnspan=2, pady=(10, 0))

        tk.Button(
            frame_botones, text="Guardar", command=self.guardar,
            bg="#17b978", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=14
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            frame_botones, text="Cancelar", command=self.destroy,
            bg="#b0b7bd", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=14
        ).pack(side=tk.LEFT, padx=5)

        self.entry_fuente.focus_set()

    def guardar(self):
        fuente = self.entry_fuente.get().strip()
        if not fuente:
            messagebox.showerror("Dato faltante", "Escribe el nombre de la fuente de emisión.", parent=self)
            return

        try:
            consumo = float(self.entry_consumo.get().replace(",", "."))
            factor = float(self.entry_factor.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error de entrada", "Consumo y factor deben ser números válidos.", parent=self)
            return

        if consumo <= 0 or factor <= 0:
            messagebox.showerror("Error de entrada", "Consumo y factor deben ser mayores que cero.", parent=self)
            return

        self.al_guardar(
            fuente, self.combo_cat.get(), consumo, factor,
            self.combo_region.get(), self.var_activo.get()
        )
        self.destroy()


class EcoAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.registros = REGISTROS_AMBIENTALES
        self.root.title("Sistema Funcional de Monitoreo Ambiental - Huella CO2")
        self.root.geometry("900x600")
        self.root.config(bg="#eef2f5")

        header = tk.Label(
            root, text="🌱 EcoAnalyzer: Procesamiento Funcional de Emisiones",
            font=("Segoe UI", 15, "bold"), bg="#1e3d59", fg="white", pady=12
        )
        header.pack(fill=tk.X)

        frame_filtros = tk.LabelFrame(root, text=" Filtros del Pipeline ", font=("Segoe UI", 10, "bold"), bg="#eef2f5", bd=1, padx=10, pady=10)
        frame_filtros.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(frame_filtros, text="Categoría:", bg="#eef2f5").grid(row=0, column=0, padx=5, sticky="e")
        self.combo_cat = ttk.Combobox(frame_filtros, values=["Todas"] + CATEGORIAS, state="readonly")
        self.combo_cat.current(0)
        self.combo_cat.grid(row=0, column=1, padx=5)

        tk.Label(frame_filtros, text="Min. CO2 (Toneladas):", bg="#eef2f5").grid(row=0, column=2, padx=5, sticky="e")
        self.entry_min = ttk.Entry(frame_filtros, width=10)
        self.entry_min.insert(0, "0.0")
        self.entry_min.grid(row=0, column=3, padx=5)

        btn_run = tk.Button(
            frame_filtros, text="⚡ Procesar Pipeline", command=self.ejecutar_pipeline,
            bg="#17b978", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, cursor="hand2"
        )
        btn_run.grid(row=0, column=4, padx=(15, 5))

        btn_add = tk.Button(
            frame_filtros, text="➕ Agregar Registro", command=self.abrir_dialogo,
            bg="#1e3d59", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, cursor="hand2"
        )
        btn_add.grid(row=0, column=5, padx=5)

        frame_tabla = tk.Frame(root, bg="#eef2f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        columnas = ("ID", "Fuente de Emisión", "Categoría", "Consumo", "Región", "Emisión CO2 (t)")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=8)

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=120)

        scroll = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        frame_metricas = tk.Frame(root, bg="#1e3d59", pady=12)
        frame_metricas.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_registros = tk.Label(frame_metricas, text="Registros Procesados: 0", font=("Segoe UI", 10), bg="#1e3d59", fg="#f5f5f5")
        self.lbl_registros.pack(side=tk.LEFT, padx=25)

        self.lbl_promedio = tk.Label(frame_metricas, text="Promedio: 0.00 t", font=("Segoe UI", 10), bg="#1e3d59", fg="#f5f5f5")
        self.lbl_promedio.pack(side=tk.LEFT, padx=25)

        self.lbl_total = tk.Label(frame_metricas, text="Total CO2: 0.00 t", font=("Segoe UI", 11, "bold"), bg="#1e3d59", fg="#ff6e40")
        self.lbl_total.pack(side=tk.RIGHT, padx=25)

        self.ejecutar_pipeline()

    def abrir_dialogo(self):
        DialogoAgregar(self.root, self.agregar)

    def agregar(self, fuente, categoria, consumo, factor, region, activo):
        nuevo = crear_registro(self.registros, fuente, categoria, consumo, factor, region, activo)
        self.registros = agregar_registro(self.registros, nuevo)
        self.ejecutar_pipeline()
        if not activo:
            messagebox.showinfo(
                "Registro inactivo",
                "El registro se guardó, pero está marcado como inactivo, por lo que no aparecerá en la tabla."
            )

    def ejecutar_pipeline(self):
        try:
            cat = self.combo_cat.get()
            umbral = float(self.entry_min.get())
        except ValueError:
            messagebox.showerror("Error de Entrada", "El valor del umbral CO2 debe ser un número válido.")
            return

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        resultados, total_co2, promedio_co2 = pipeline_eco_analyzer(self.registros, cat, umbral)

        for r in resultados:
            self.tabla.insert("", tk.END, values=(
                r["id"], r["fuente"], r["categoria"], f"{r['consumo']:,}", r["region"], f"{r['co2_toneladas']} t"
            ))

        self.lbl_registros.config(text=f"Registros Procesados: {len(resultados)}")
        self.lbl_promedio.config(text=f"Promedio Emisión: {promedio_co2:.2f} t")
        self.lbl_total.config(text=f"Total CO2 Generado: {total_co2:.2f} t")


if __name__ == "__main__":
    root = tk.Tk()
    app = EcoAnalyzerApp(root)
    root.mainloop()