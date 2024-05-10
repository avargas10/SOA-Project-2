import tkinter as tk
from tkinter import Label, Entry, Button, Listbox, Scrollbar, END, messagebox, filedialog
import plotly.express as px
import json
from scheduler import Scheduler
from cpu import CPU
import subprocess
from rms import RateMonotonicScheduler
from edf import EarliestDeadlineFirstScheduler
from task import Task

class gui():
    def __init__(self, root):
        self.root = root
        self.root.title("Task Scheduler GUI")
        self.scheduler = None
        
        
        self.setup_initial_choice()

    def setup_initial_choice(self):
        Button(self.root, text="Run Manually", command=self.setup_manual_operation).pack(pady=20)
        Button(self.root, text="Provide CLI Command", command=self.provide_cli_command).pack(pady=20)
        Button(self.root, text="Help", command=self.display_help).pack(pady=20)

    def provide_cli_command(self):
        self.clear_widgets()
        Label(self.root, text="Enter CLI Command:").pack()
        self.cli_command_entry = Entry(self.root, width=50)
        self.cli_command_entry.pack(pady=10)
        Button(self.root, text="Execute Command", command=self.execute_cli_command).pack(pady=10)

    def execute_cli_command(self):
        command = self.cli_command_entry.get()
        try:
            output = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            messagebox.showinfo("CLI Command Output", output.stdout)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Command failed: {e.stderr}")

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_manual_operation(self):
        self.clear_widgets()
        Label(self.root, text="Scheduler Type (RMS/EDF):").pack()
        self.scheduler_type_entry = Entry(self.root)
        self.scheduler_type_entry.pack()
        
        Label(self.root, text="Simulation Time (seconds):").pack()
        self.simulation_time_entry = Entry(self.root)
        self.simulation_time_entry.pack()

        Button(self.root, text="Submit", command=self.submit_manual_setup).pack(pady=20)

        
        self.task_list = Listbox(self.root, height=10, width=50)
        self.task_list.pack(pady=20)

    def submit_manual_setup(self):
        scheduler_type = self.scheduler_type_entry.get()
        simulation_time = int(self.simulation_time_entry.get())
        cpu = CPU("Processor") 

        if scheduler_type == 'RMS':
            self.scheduler = RateMonotonicScheduler(simulation_time, scheduler_type, cpu)
        elif scheduler_type == 'EDF':
            self.scheduler = EarliestDeadlineFirstScheduler(simulation_time, scheduler_type, cpu)
        
        self.setup_task_management_ui()

    def setup_task_management_ui(self):
        
        self.clear_widgets()
        Label(self.root, text="Task ID:").pack()
        self.task_id_entry = Entry(self.root)
        self.task_id_entry.pack()

        Label(self.root, text="Period:").pack()
        self.task_period_entry = Entry(self.root)
        self.task_period_entry.pack()

        Label(self.root, text="Deadline:").pack()
        self.task_deadline_entry = Entry(self.root)
        self.task_deadline_entry.pack()

        Label(self.root, text="Execution Time:").pack()
        self.task_execution_time_entry = Entry(self.root)
        self.task_execution_time_entry.pack()

        Button(self.root, text="Add Task", command=self.add_task).pack(pady=10)
        Button(self.root, text="Run Scheduler", command=self.run_scheduler).pack(pady=10)
        Button(self.root, text="Load and Plot Timeline", command=self.load_and_plot_timeline).pack(pady=10)

        
        self.task_list = Listbox(self.root, height=10, width=50)
        self.task_list.pack(pady=20)

    def add_task(self):
        task_id = self.task_id_entry.get().strip()
        period = int(self.task_period_entry.get())
        deadline = int(self.task_deadline_entry.get())
        execution_time = int(self.task_execution_time_entry.get())
        
        if not task_id:
            messagebox.showerror("Error", "Task ID cannot be empty.")
            return

        task = Task(task_id, period, deadline, execution_time)
        self.scheduler.add_task(task)
        
        # Update the task list visually
        task_info = f"{task_id}, Period: {period}, Deadline: {deadline}, Exec Time: {execution_time}"
        self.task_list.insert(END, task_info)

        messagebox.showinfo("Task Added", f"Task {task_id} added successfully.")

    def display_help(self):
        # Muestra información de ayuda
        help_text = ("Información de Ayuda:\n\n"
                     "Para agregar una tarea:\n"
                     "- Ingrese el ID de la tarea, periodo, plazo y tiempo de ejecución.\n"
                     "- Haga clic en 'Agregar Tarea' para programarla.\n\n"
                     "Para ejecutar el programador:\n"
                     "- Asegúrese de que todas las tareas estén agregadas.\n"
                     "- Haga clic en 'Ejecutar Programador' para comenzar la simulación.\n\n"
                     "Comando CLI:\n"
                     "- Proporcione un comando de línea de comandos como lo haría en una terminal para ejecutar tareas de programación.\n"
                     "  Ejemplo: cli_handler.py -i input.txt -o output.txt -a RMS -t 100")
        messagebox.showinfo("Ayuda", help_text)

    def run_scheduler(self):
        self.scheduler.run()
        messagebox.showinfo("Scheduler", "Scheduler has been run.")

    def load_and_plot_timeline(self):
        file_path = filedialog.askopenfilename(title="Select file", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        with open(file_path, 'r') as file:
            data = json.load(file)
        self.plot_timeline(data)

    def plot_timeline(self, data):
        df = []
        colors = {}
        color_pal = px.colors.qualitative.Plotly
        color_idx = 0
        for task in data['Tasks']:
            start = int(task['Start'])
            finish = int(task['Finish'])
            if task['Task'] not in colors:
                colors[task['Task']] = color_pal[color_idx % len(color_pal)]
                color_idx += 1
            df.append(dict(Task=task['Task'], Start=start, Finish=finish, Color=colors[task['Task']]))
        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Task", color_discrete_map=colors)
        fig.update_yaxes(categoryorder="total ascending")
        fig.update_layout(showlegend=True)
        fig.show()
