import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import Counter

# ---------------------------
# GENERALIZATION FUNCTIONS
# ---------------------------
def generalize_age(age, level):
    if level == 0: return age
    elif level == 1: return (age // 5) * 5
    elif level == 2: return (age // 10) * 10
    else: return "*"

def generalize_postal(pc, level):
    pc = str(pc)
    if level == 0: return pc
    elif level == 1: return pc[:3] + "**"
    elif level == 2: return pc[:2] + "***"
    else: return "*"

def generalize_cat(val, level):
    return val if level == 0 else "*"

# ---------------------------
# EVALUATION METRICS (VERSIÓN SENSIBLE)
# ---------------------------
def calculate_metrics(df_original, df_anonymized, qi, level):
    # 1. Re-identification Risk (Basado en el tamaño real de los grupos)
    # A grupos más grandes, el riesgo baja significativamente.
    sizes = df_anonymized.groupby(qi).size()
    avg_group_size = sizes.mean()
    risk = 1 / avg_group_size if avg_group_size > 0 else 1
    
    # 2. Information Loss (Basado en la severidad de la generalización)
    # Nivel 0: 0% | Nivel 1: 33% | Nivel 2: 66% | Nivel 3: 100%
    info_loss = level / 3.0
    
    return risk, info_loss

# ---------------------------
# PRIVACY MODELS
# ---------------------------
def check_k(df, qi, k):
    return df.groupby(qi).size().min() >= k

def check_l(df, qi, sensitive, l):
    for _, g in df.groupby(qi):
        if g[sensitive].nunique() < l: return False
    return True

def distribution(series):
    total = len(series)
    counts = Counter(series)
    return {k: v / total for k, v in counts.items()}

def distance(p, q):
    keys = set(p.keys()).union(q.keys())
    return sum(abs(p.get(k, 0) - q.get(k, 0)) for k in keys) / 2

def check_t(df, qi, sensitive, t):
    global_dist = distribution(df[sensitive])
    for _, g in df.groupby(qi):
        local_dist = distribution(g[sensitive])
        if distance(global_dist, local_dist) > t: return False
    return True

# ---------------------------
# ANONYMIZATION ENGINE (AJUSTADO)
# ---------------------------
def anonymize(df, qi, sensitive, method, k, l, t):
    # Guardamos copia del original para comparar
    df_original_qi = df[qi].copy()
    
    # Probamos niveles de generalización 
    for level in range(4):
        temp = df.copy()
        
        # Aplicamos generalización según el nivel actual
        temp["age"] = temp["age"].apply(lambda x: generalize_age(x, level))
        temp["postal_code"] = temp["postal_code"].apply(lambda x: generalize_postal(x, level))

        for col in qi:
            if col not in ["age", "postal_code"]:
                temp[col] = temp[col].apply(lambda x: generalize_cat(x, level))

        # --- VALIDACIÓN DE MODELOS ---
        ok = False
        if method == "k":
            ok = check_k(temp, qi, k)
        elif method == "l":
            ok = check_l(temp, qi, sensitive, l)
        elif method == "t":
            # Para t, si el usuario pone un valor > 1, lo tratamos como decimal (ej: 10 -> 0.1)
            t_val = t if t <= 1 else t / 100
            ok = check_t(temp, qi, sensitive, t_val)

        if ok:
            # Si cumple, calculamos métricas de ese nivel específico
            risk, loss = calculate_metrics(df_original_qi, temp, qi, level)
            return temp, risk, loss, level

    return None

# ---------------------------
# GUI
# ---------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Anonymizer Evaluation Tool")
        self.root.geometry("420x580")
        
        tk.Label(root, text="Data Anonymization System", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Button(root, text="Load Dataset (CSV)", command=self.load_file).pack(pady=5)
        self.label_file = tk.Label(root, text="No file...", fg="grey"); self.label_file.pack()

        tk.Label(root, text="Privacy Method (k, l, t):").pack(pady=(10,0))
        self.method_entry = tk.Entry(root, justify='center'); self.method_entry.insert(0, "k"); self.method_entry.pack()

        tk.Label(root, text="Parameters (k, l, t):").pack()
        self.k_e = tk.Entry(root, justify='center'); self.k_e.insert(0, "5"); self.k_e.pack()
        self.l_e = tk.Entry(root, justify='center'); self.l_e.insert(0, "2"); self.l_e.pack()
        self.t_e = tk.Entry(root, justify='center'); self.t_e.insert(0, "0.2"); self.t_e.pack()

        tk.Button(root, text="RUN ANONYMIZATION", bg="#2196F3", fg="white", command=self.run).pack(pady=20)

        self.res_frame = tk.LabelFrame(root, text="Evaluation Criteria Results", padx=10, pady=10)
        self.res_frame.pack(padx=20, fill="both")

        self.risk_label = tk.Label(self.res_frame, text="Re-identification Risk: -", font=("Courier", 10))
        self.risk_label.pack(anchor="w")
        self.loss_label = tk.Label(self.res_frame, text="Information Loss: -", font=("Courier", 10))
        self.loss_label.pack(anchor="w")
        self.level_label = tk.Label(self.res_frame, text="Generalization level: -", font=("Courier", 10))
        self.level_label.pack(anchor="w")

    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.file_path: self.label_file.config(text=self.file_path, fg="black")

    def run(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            messagebox.showwarning("Error", "Load a file first"); return

        try:
            df = pd.read_csv(self.file_path)
            
            # Preproceso estándar
            df["age"] = pd.to_datetime(df["date_of_birth"], format="mixed", errors="coerce").dt.year
            df = df.dropna(subset=["age"])
            df["age"] = 2026 - df["age"] 
            
            df.drop(columns=["name", "email", "date_of_birth"], inplace=True, errors='ignore')

            qi = ["age", "gender", "postal_code", "degree_program"]
            sensitive = "medical_indicator"

            res = anonymize(df, qi, sensitive, 
                            self.method_entry.get().lower(), 
                            int(self.k_e.get()), int(self.l_e.get()), float(self.t_e.get()))

            if res:
                df_final, risk, loss, lvl = res
                self.risk_label.config(text=f"Re-identification Risk: {risk:.5f}", fg="red")
                self.loss_label.config(text=f"Information Loss: {loss:.2%}", fg="blue")
                self.level_label.config(text=f"Generalization level: {lvl}")
                
                path = filedialog.asksaveasfilename(defaultextension=".csv")
                if path: df_final.to_csv(path, index=False)
            else:
                messagebox.showwarning("Failed", "No level of generalization satisfies the parameters.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()