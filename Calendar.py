import tkinter as tk
from tkinter import ttk, simpledialog
import calendar
import json
import os
from datetime import datetime
import sys


class CustomCalendar:
    def __init__(self, root):
        self.root = root
        self.root.title("Calendário Personalizado")

        # Ajusta os caminhos para os arquivos JSON
        self.adjust_file_paths()

        self.load_notes()
        self.load_window_config()

        self.root.configure(bg='#2e2e2e')  # Modo escuro

        # Obter o mês e ano atuais
        today = datetime.today()
        self.year_var = tk.IntVar(value=today.year)
        self.month_var = tk.IntVar(value=today.month)

        # Seletor de ano
        ttk.Label(root, text="Ano:", background='#2e2e2e', foreground='white').pack(pady=5)
        self.year_entry = ttk.Entry(root, textvariable=self.year_var)
        self.year_entry.pack(pady=5)

        # Seletor de mês
        ttk.Label(root, text="Mês:", background='#2e2e2e', foreground='white').pack(pady=5)
        self.month_entry = ttk.Entry(root, textvariable=self.month_var)
        self.month_entry.pack(pady=5)

        # Botão para atualizar calendário
        self.update_button = ttk.Button(root, text="Atualizar Calendário", command=self.update_calendar)
        self.update_button.pack(pady=5)

        # Frame para o calendário
        self.cal_frame = tk.Frame(root, background='#2e2e2e')
        self.cal_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Configuração de redimensionamento
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.cal_frame.grid_rowconfigure(0, weight=1)
        for i in range(7):
            self.cal_frame.grid_columnconfigure(i, weight=1)

        self.update_calendar()

        # Salvar configuração ao fechar a janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Centralizar a janela com dimensões específicas
        self.center_window()  # Centraliza a janela com as dimensões carregadas

    def adjust_file_paths(self):
        """Ajusta os caminhos dos arquivos de dados para o diretório correto."""
        base_path = os.path.dirname(sys.argv[0]) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
        self.data_file = os.path.join(base_path, "calendar_data.json")
        self.config_file = os.path.join(base_path, "window_config.json")

    def load_notes(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                self.notes = json.load(file)
        else:
            self.notes = {}

    def load_window_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                config = json.load(file)
                self.root.geometry(f"{config['width']}x{config['height']}")
                self.root.update_idletasks()  # Atualiza a janela para obter dimensões corretas
        else:
            self.root.geometry("1200x800")  # Dimensões padrão

    def save_window_config(self):
        config = {
            "width": self.root.winfo_width(),
            "height": self.root.winfo_height()
        }
        with open(self.config_file, 'w') as file:
            json.dump(config, file)

    def save_notes(self):
        with open(self.data_file, 'w') as file:
            json.dump(self.notes, file)

    def update_calendar(self):
        for widget in self.cal_frame.winfo_children():
            widget.destroy()

        year = self.year_var.get()
        month = self.month_var.get()
        cal = calendar.Calendar(firstweekday=0)

        days = cal.itermonthdays(year, month)
        day_names = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

        # Adicionar nomes dos dias da semana
        for col, day_name in enumerate(day_names):
            day_label = tk.Label(self.cal_frame, text=day_name, bg="#1c1c1c", fg="white", borderwidth=1, relief="solid")
            day_label.grid(row=0, column=col, sticky='nsew', padx=5, pady=5)

        row = 1
        col = 0
        today = datetime.today()
        today_str = today.strftime(f"{year}-{month:02}-%d")

        for day in days:
            if day == 0:
                col += 1
                if col == 7:
                    col = 0
                    row += 1
                continue

            day_str = f"{year}-{month:02}-{day:02}"
            note = self.notes.get(day_str, "")
            note_color = "white"
            if note:
                # Determinar a cor da anotação com base no valor
                try:
                    value = float(note.split()[0].replace("$", "").replace(",", ""))
                    if value > 0:
                        note_color = "#32CD32"  # Verde limão para valores positivos
                    elif value < 0:
                        note_color = "#FF4500"  # Vermelho para valores negativos
                except ValueError:
                    pass

            # Verifica se é o dia atual e aplica contorno azul bebê
            relief = "solid" if day_str == today.strftime("%Y-%m-%d") else "flat"
            day_label = tk.Label(
                self.cal_frame,
                text=f"{day}\n{note}",
                bg="#3a3a3a",
                fg=note_color,
                borderwidth=1,
                relief=relief,
                highlightbackground="#87CEFA" if day_str == today.strftime("%Y-%m-%d") else "#3a3a3a",
                highlightcolor="#87CEFA" if day_str == today.strftime("%Y-%m-%d") else "#3a3a3a",
                highlightthickness=2 if day_str == today.strftime("%Y-%m-%d") else 0
            )
            day_label.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
            day_label.bind("<Double-Button-1>", lambda event, date=day_str: self.add_note_for_date(date))
            col += 1
            if col == 7:
                col = 0
                row += 1

        # Configuração de redimensionamento para cada linha
        for i in range(1, row + 1):
            self.cal_frame.grid_rowconfigure(i, weight=1)

    def add_note_for_date(self, date):
        note = simpledialog.askstring("Adicionar Nota", f"Adicionar nota para {date}:")
        if note is not None:
            self.notes[date] = note
            self.save_notes()  # Salva as notas após adicionar
            self.update_calendar()

    def on_closing(self):
        self.save_window_config()
        self.save_notes()  # Salvar notas antes de fechar
        self.root.destroy()

    def center_window(self):
        """Centraliza a janela no monitor e define dimensões específicas."""
        self.root.update_idletasks()  # Atualiza o estado da janela antes de calcular dimensões
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.root.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CustomCalendar(root)
    root.mainloop()
