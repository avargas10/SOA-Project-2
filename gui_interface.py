import tkinter as tk
from tkinter import Label, Entry, Button, Listbox, Scrollbar, END, messagebox, filedialog, Toplevel, Text, simpledialog
import plotly.express as px
import tkinterweb
import json
import shlex
import argparse
from scheduler import Scheduler
from cpu import CPU
import subprocess
from rms import RateMonotonicScheduler
from edf import EarliestDeadlineFirstScheduler
from task import Task
import random
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from constants import LOGS_PATH
from file_manager import read_tasks_from_file, write_statistics_to_file

class gui():
    def __init__(self, root):
        self.root = root
        self.root.title("Task Scheduler Simulation Interface")
        self.cpu = CPU("Processor")
        self.random_case = tk.IntVar()
        self.scheduler = None
        self.task_ids = set()
        self.setup_initial_choice()
        

    def setup_initial_choice(self):
        self.clear_widgets()  # Ensure the window is cleared whenever setting up the initial choice
        Button(self.root, text="Manual Run", command=self.setup_manual_operation).pack(pady=20)
        Button(self.root, text="CLI Command", command=self.provide_cli_command).pack(pady=20)
        Button(self.root, text="Help", command=lambda: self.display_help(context="main")).pack(pady=20)

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()
         # Immediately reinitialize CPU with default settings

    def provide_cli_command(self):
        self.clear_widgets()
        Label(self.root, text="Enter CLI Command:").pack()
        self.cli_command_entry = Entry(self.root, width=80)
        self.cli_command_entry.pack(pady=10)
        Button(self.root, text="Execute Command", command=self.execute_cli_command).pack(pady=10)
        Button(self.root, text="View Statistics", command=self.view_statistics).pack(pady=10)
        Button(self.root, text="View Timeline", command=self.load_and_plot_timeline).pack(pady=10)
        Button(self.root, text="Clear Simulation", command=self.clear_all_tasks).pack(pady=20)
        Button(self.root, text="Help", command=lambda: self.display_help(context="cli_command")).pack(pady=20)

    def view_statistics(self):
        # Read log content
        try:
            with open(LOGS_PATH + self.scheduler.logPath + "-statistics.log", 'r') as file:
                log_content = file.read()
            # Create a new window to display log content
            log_window = Toplevel(self.root)
            log_window.title("Statistics Log")
            text = Text(log_window, wrap='word')
            text.insert('end', log_content)
            text.pack(expand=True, fill='both')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read log file: {str(e)}")    

    def execute_cli_command(self):
            command_line = self.cli_command_entry.get()
            args = self.parse_command(command_line)
            aperiodic = False
            if args:
                if args.algorithm == 'RMS':
                    self.scheduler = RateMonotonicScheduler(args.time, args.algorithm, self.cpu)
                elif args.algorithm == 'EDF':
                    self.scheduler = EarliestDeadlineFirstScheduler(args.time, args.algorithm, self.cpu)
                elif args.algorithm == 'EDFA':
                    self.scheduler = EarliestDeadlineFirstScheduler(args.time, args.algorithm, self.cpu, aperiodic=True, randomGenerator=args.random)  
                    print(self.scheduler.name)    
                tasks = read_tasks_from_file(args.input, aperiodic=aperiodic)
                for task in tasks:
                   self.scheduler.add_task(task)
                self.scheduler.run()
                statistics = self.scheduler.get_statistics()
                write_statistics_to_file(args.output, statistics)
                messagebox.showinfo("Success", "Scheduler ran successfully and results saved.")
            else:
                messagebox.showerror("Error", "Failed to parse the command or initialize the scheduler.")

    def parse_command(self, command_line):
        parser = argparse.ArgumentParser(description='Simulador de Scheduling de Tiempo Real')
        parser.add_argument('-i', '--input', type=str, required=True, help='Archivo de entrada con tareas')
        parser.add_argument('-o', '--output', type=str, required=True, help='Archivo de salida para estadísticas')
        parser.add_argument('-a', '--algorithm', type=str, required=True, choices=['RMS', 'EDF', 'EDFA'], help='Algoritmo de scheduling')
        parser.add_argument('-t', '--time', type=int, required=True, help='Tiempo de simulación')
        parser.add_argument('-r', '--random', type=bool, required=False, help='Random Init Times')

        try:
            args = parser.parse_args(shlex.split(command_line))
            print(args)
            return args
        except SystemExit:
            # Handle the parsing errors and exit gracefully without crashing the GUI
            return None


    def setup_manual_operation(self):
        self.clear_widgets()
        Label(self.root, text="Scheduler Type (RMS/EDF/EDFA):").pack()
        self.scheduler_type_entry = Entry(self.root)
        self.scheduler_type_entry.pack()
        
        Label(self.root, text="Simulation Time (seconds):").pack()
        self.simulation_time_entry = Entry(self.root)
        self.simulation_time_entry.pack()

        tk.Checkbutton(self.root, text="Real Random Interruptions Case", variable=self.random_case).pack()
        Button(self.root, text="Submit", command=self.submit_manual_setup).pack(pady=20)

        
        self.task_list = Listbox(self.root, height=10, width=50)
        self.task_list.pack(pady=20)

    def submit_manual_setup(self):
        scheduler_type = self.scheduler_type_entry.get()
        simulation_time = int(self.simulation_time_entry.get())
        random_case = int(self.random_case.get()) > 0
        if scheduler_type == 'RMS':
            self.scheduler = RateMonotonicScheduler(simulation_time, scheduler_type, self.cpu)
        elif scheduler_type == 'EDF':
            self.scheduler = EarliestDeadlineFirstScheduler(simulation_time, scheduler_type, self.cpu)
        elif scheduler_type == 'EDFA':
            self.scheduler = EarliestDeadlineFirstScheduler(simulation_time, scheduler_type, self.cpu, aperiodic=True, randomGenerator=random_case)    
        
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
        Button(self.root, text="Run Simulation", command=self.run_scheduler).pack(pady=10)
        Button(self.root, text="View Statistics", command=self.view_statistics).pack(pady=10)
        Button(self.root, text="View Timeline", command=self.load_and_plot_timeline).pack(pady=10)
        Button(self.root, text="Clear Simulation", command=self.clear_all_tasks).pack(pady=20)
        Button(self.root, text="Help", command=lambda: self.display_help(context="manual_run")).pack(pady=20)
        
        self.task_list = Listbox(self.root, height=10, width=50)
        self.task_list.pack(pady=20)

    def clear_all_tasks(self):
        # This resets the entire application to the initial choice screen
        self.scheduler = None
        self.cpu = CPU("Processor")
        self.task_ids.clear()
        self.setup_initial_choice()

    def add_task(self):
            task_id = self.task_id_entry.get().strip()
            if not task_id:
                messagebox.showerror("Error", "Task ID cannot be empty.")
                return

            if task_id in self.task_ids:
                messagebox.showerror("Error", "Task ID must be unique.")
                return

            try:
                period = int(self.task_period_entry.get())
                deadline = int(self.task_deadline_entry.get())
                execution_time = int(self.task_execution_time_entry.get())
                task = Task(pid=task_id, period=period, deadline=deadline, execution_time=execution_time)
                self.scheduler.add_task(task)
                self.task_ids.add(task_id)  # Add the TaskID to the set of existing IDs
                
                # Update the task list visually
                task_info = f"{task_id}, Period: {period}, Deadline: {deadline}, Exec Time: {execution_time}"
                self.task_list.insert(END, task_info)
                messagebox.showinfo("Task Added", f"Task {task_id} added successfully.")
            
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input for task parameters: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def display_help(self, context):
        if context == 'main':
            help_text = ("Información de Ayuda:\n\n"
                        "Menu Principal, cuenta con 2 opciones a ecoger:\n"
                        "- Manual Run: Esta opción le permite crear la simulación de forma manual, definir el tipo de scheduler, tiempo de ejecución," 
                            "asi como agregar las tarea 1 a 1, tambien nos permite ejecutar el Scheduler y ver estadisticas y linea del tiempo.\n"
                        "- CLI Command: Esta opcion le permite ejecutar un comando de CLI, para cargar la simulación desde archivos de entradas y guardar salidas en archivos.\n"
                        "    Referirse al help de la siguiente pantalla de esta opción para mas detalles \n")

        elif context == 'cli_command':
             help_text =  ("Ayuda para Comando CLI:\n\n"
                "Proporcione un comando que ejecutará una simulación completa basada en los parámetros especificados. "
                "El comando debe contener los parámetros necesarios para ejecutar la simulación.\n\n"
                "Ejemplo de comando:\n"
                "-i examples/task1.txt -o results/test1_result_rms.txt -a RMS -t 80\n\n"
                "Descripción de los parámetros del comando:\n"
                "-i: Archivo de entrada que contiene las tareas. Cada tarea debe estar en el formato 'ID_Tarea, Periodo, Tiempo_de_ejecución, Plazo'.\n"
                "    Ejemplo de tareas en el archivo:\n"
                "    Task1,10,4,8\n"
                "    Task2,15,5,7\n"
                "    Task3,20,8,10\n"
                "-o: Ruta del archivo donde se deben almacenar los resultados de la simulación.\n"
                "-a: Algoritmo de planificación a utilizar. Las opciones disponibles son: RMS, EDF, EDFA.\n"
                "-t: Tiempo de ejecución de la simulación en segundos, indica cuánto tiempo debe correr la simulación.\n\n"
                "Descripción de los botones disponibles:\n"
                "Run Command: Ejecuta el comando proporcionado y realiza la simulación según los parámetros dados.\n"
                "View Time Line: Muestra una línea de tiempo con la ejecución de las tareas en el CPU. Este toma por defecto el valor del parámetro -t, "
                "sin embargo, puede ser modificado en el cuadro de texto correspondiente.\n"
                "View Statistics: Muestra las estadísticas de ejecución por proceso, incluyendo números y porcentajes de ejecuciones, "
                "missed deadlines, etc. Este es un archivo formateado en JSON.\n"
                "Clear Simulation: Reinicia la ejecución para comenzar de nuevo, eliminando cualquier tarea y resultado previamente cargados.\n")
        elif context == 'manual_run':
             help_text =  ("Ayuda para Manual Run:\n\n"
                "Esta interfaz le permite Agregar y Calenderizar Tasks de forma manual e interactiva\n\n"
                "Para Agregar un Task debe primero proporcionar:\n"
                "TaskId: Id Unico de la tarea. No puede ser repetido o econtrará un error.\n"
                "Period: Periodo de la Tarea.\n"
                "Deadline: Deadline.\n"
                "Execution Time: Tiempo de ejecución de la tarea.\n"

                "Una vez lleno este campo, debe presionar el botton Add Task, lo que agregará la tarea a la simulacion, esto se puede repetir muchas veces.\n\n"
                "Run Simulation: Corre el Scheduler, con el Algoritmo seleccionado en la pantalla anterio, y por el tiempo definido.\n"
                "View Time Line: Muestra una línea de tiempo con la ejecución de las tareas en el CPU. Este toma por defecto el valor del parámetro -t, "
                "sin embargo, puede ser modificado en el cuadro de texto correspondiente.\n"
                "View Statistics: Muestra las estadísticas de ejecución por proceso, incluyendo números y porcentajes de ejecuciones, "
                "missed deadlines, etc. Este es un archivo formateado en JSON.\n"
                "Clear Simulation: Reinicia la ejecución para comenzar de nuevo, eliminando cualquier tarea y resultado previamente cargados.\n")
        else:
            help_text = "No help available for this section."
        messagebox.showinfo("Ayuda", help_text)

    def run_scheduler(self):
        self.scheduler.run()
        messagebox.showinfo("Scheduler", "Scheduler has been run.")
   
    def get_task_history(self):
        # Directly use the CPU instance of the gui class
        if hasattr(self, 'cpu'):
            return self.cpu.return_cpu_history()
        else:
            messagebox.showerror("Error", "CPU not initialized.")
            return []

   
    def get_timeline_scale(self):
        timeline_scale = tk.simpledialog.askinteger("Timeline Scale", "Enter the timeline scale (seconds):", initialvalue=self.scheduler.simulation_time)
        if timeline_scale is None:
            timeline_scale = self.scheduler.simulation_time  # default to simulation time if nothing is entered
        return timeline_scale
    

    def plot_tasks(self, task_history, timeline_scale):
        # Filtering out entries where 'Task' is None if not meaningful for visualization
        filtered_history = [task for task in task_history if task['Task'] is not None]

        if not filtered_history:
            messagebox.showinfo("No Data", "No valid task history to display.")
            return

        # Prepare data
        df = pd.DataFrame(filtered_history)
        unique_tasks = df['Task'].unique()
        colors = {task: (random.random(), random.random(), random.random()) for task in unique_tasks}  # RGB colors

        # Create a Gantt chart using matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))  # Adjust size as needed
        yticks = []
        yticklabels = []

        for i, task in enumerate(sorted(unique_tasks, reverse=True)):
            task_data = df[df['Task'] == task]
            y_position = 10 * (i + 1)
            yticks.append(y_position + 5)  # Center of the bar
            yticklabels.append(f"Task {task}")

            for _, row in task_data.iterrows():
                start = row['Start']
                finish = row['Finish']
                ax.broken_barh([(start, finish - start)], (y_position, 9), facecolors=colors[task])

        # Set labels and limits
        ax.set_ylim(5, 10 * len(unique_tasks) + 5)
        ax.set_xlim(0, timeline_scale)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Tasks')
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)
        ax.grid(True)
        
        # Show plot
        plt.title("Task Execution Timeline")
        plt.tight_layout()  # Adjust layout to make room for label
        plt.show()

    def load_and_plot_timeline(self):
        if not self.scheduler or not hasattr(self.scheduler, 'cpu'):
            messagebox.showerror("Error", "Scheduler or CPU not initialized.")
            return
        
        task_history = self.get_task_history()
        if not task_history:
            messagebox.showinfo("Info", "No task history available.")
            return

        timeline_scale = self.get_timeline_scale()
        self.plot_tasks(task_history, timeline_scale)
