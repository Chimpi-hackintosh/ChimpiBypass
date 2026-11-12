"""ChimpiBypass 1.0.0 - experimental per-app Mesa3D manager."""
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from bypass_files import install_mesa_files, restore_mesa_files

class ChimpiBypass(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChimpiBypass 1.0.0")
        self.geometry("720x390")
        self.exe = tk.StringVar()
        self.mesa = tk.StringVar()
        self.status = tk.StringVar(value="Escolha um executável e as bibliotecas Mesa3D")
        ttk.Label(self, text="ChimpiBypass 1.0.0", font=("Segoe UI", 20, "bold")).pack(padx=20, pady=12)
        self.choose("Aplicativo Windows (.exe)", self.exe, self.find_exe)
        self.choose("Pasta das DLLs Mesa3D", self.mesa, self.find_mesa)
        bar = ttk.Frame(self)
        bar.pack(padx=20, pady=14)
        for label, fn in (("Instalar", self.install), ("Restaurar", self.restore), ("Abrir aplicativo", self.launch)):
            ttk.Button(bar, text=label, command=fn).pack(side="left", padx=6)
        ttk.Label(self, textvariable=self.status, wraplength=650).pack(padx=20, pady=10)
        ttk.Label(self, text="Experimental: não modifica drivers ou System32. Use DLLs confiáveis e de arquitetura compatível.", wraplength=660).pack(pady=8)

    def choose(self, label, variable, command):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=20, pady=6)
        ttk.Label(frame, text=label).pack(anchor="w")
        line = ttk.Frame(frame)
        line.pack(fill="x")
        ttk.Entry(line, textvariable=variable).pack(side="left", fill="x", expand=True)
        ttk.Button(line, text="Procurar", command=command).pack(side="left", padx=6)

    def find_exe(self):
        p = filedialog.askopenfilename(filetypes=[("Aplicativos", "*.exe")])
        if p: self.exe.set(p)

    def find_mesa(self):
        p = filedialog.askdirectory()
        if p: self.mesa.set(p)

    def target(self):
        p = Path(self.exe.get()).resolve()
        if not p.is_file() or p.suffix.lower() != ".exe":
            raise ValueError("Selecione um .exe válido")
        if any(s.lower() in ("windows", "system32", "syswow64") for s in p.parts):
            raise ValueError("Não modifique pastas do sistema Windows")
        return p

    def install(self):
        try:
            exe = self.target()
            if not messagebox.askyesno("Confirmar", "Instalar DLLs apenas na pasta do aplicativo?"):
                return
            install_mesa_files(exe, Path(self.mesa.get()))
            self.status.set("DLLs instaladas somente na pasta do aplicativo")
        except Exception as e:
            messagebox.showerror("Falha", str(e))

    def restore(self):
        try:
            exe = self.target()
            if not messagebox.askyesno("Confirmar", "Restaurar arquivos anteriores?"):
                return
            restore_mesa_files(exe)
            self.status.set("Restauração concluída")
        except Exception as e:
            messagebox.showerror("Falha", str(e))

    def launch(self):
        try:
            exe = self.target()
            subprocess.Popen([str(exe)], cwd=str(exe.parent))
            self.status.set(f"Iniciado: {exe.name}")
        except Exception as e:
            messagebox.showerror("Falha", str(e))

if __name__ == "__main__":
    ChimpiBypass().mainloop()
