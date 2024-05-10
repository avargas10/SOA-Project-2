import tkinter as tk
from tkinter import Label, Entry, Button, Listbox, Scrollbar, END, messagebox, filedialog, Toplevel, Text, simpledialog
import plotly.express as px
import tkinterweb
import json
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

class gui():
    def __init__(self, root):
        self.root = root
        self.root.title("Task Scheduler GUI")
        self.cpu = CPU("Processor")
        self.scheduler = None
        self.task_ids = set()
        self.setup_initial_choice()
        
        
        self.setup_initial_choice()

    def setup_initial_choice(self):
        self.clear_widgets()  # Ensure the window is cleared whenever setting up the initial choice
        Button(self.root, text="Run Manually", command=self.setup_manual_operation).pack(pady=20)
        Button(self.root, text="Provide CLI Command", command=self.provide_cli_command).pack(pady=20)
        Button(self.root, text="Help", command=self.display_help).pack(pady=20)

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def provide_cli_command(self):
        self.clear_widgets()
        Label(self.root, text="Enter CLI Command:").pack()
        self.cli_command_entry = Entry(self.root, width=50)
        self.cli_command_entry.pack(pady=10)
        Button(self.root, text="Execute Command", command=self.execute_cli_command).pack(pady=10)
        Button(self.root, text="View Timeline", command=self.load_and_plot_timeline).pack(pady=10)
        Button(self.root, text="View Statistics", command=self.view_statistics).pack(pady=10)
        Button(self.root, text="Clear All Tasks", command=self.setup_initial_choice).pack(pady=10)

    def view_statistics(self):
        # Read log content
        try:
            with open('logs/log-scheduler-RMS-statistics.log', 'r') as file:
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
        command = self.cli_command_entry.get()
        try:
            output = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            messagebox.showinfo("CLI Command Output", "Command executed successfully, check output files for details")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Command failed: {e.stderr}")

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_manual_operation(self):
        self.clear_widgets()
        Label(self.root, text="Scheduler Type (RMS/EDF/EDFA):").pack()
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

        if scheduler_type == 'RMS':
            self.scheduler = RateMonotonicScheduler(simulation_time, scheduler_type, self.cpu)
        elif scheduler_type == 'EDF':
            self.scheduler = EarliestDeadlineFirstScheduler(simulation_time, scheduler_type, self.cpu)
        elif scheduler_type == 'EDFA':
            self.scheduler = EarliestDeadlineFirstScheduler(simulation_time, scheduler_type, self.cpu)    
        
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
        Button(self.root, text="Clear All Tasks", command=self.clear_all_tasks).pack(pady=20)
        
        self.task_list = Listbox(self.root, height=10, width=50)
        self.task_list.pack(pady=20)

    def clear_all_tasks(self):
        # This resets the entire application to the initial choice screen
        self.scheduler = None
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

                task = Task(task_id, period, deadline, execution_time)
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
