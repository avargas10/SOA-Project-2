import pandas as pd
from datetime import datetime, timedelta
from tabulate import tabulate
from logger import Logger
from constants import CPU_LOGGER
class CPU:
    def __init__(self, name):
        self.name = name
        self.current_task = None
        self.execution_history = []
        self.preemp = True
        self.logPath = CPU_LOGGER + "-" + name
        self.logger = Logger(self.logPath, clean=True) 
        
    def run_task(self, task, current_time):
        history_entry =  {"Task": task.pid , "Start": current_time, "Finish": current_time + 1}
        self.execution_history.append(history_entry)
        self.current_task = task
        finished = task.run(current_time)
        if finished:
            self.current_task = None
        return task, finished
    
    def empty_run(self, current_time):
        self.current_task = None
        history_entry =  {"Task": self.current_task , "Start": current_time, "Finish": current_time + 1}
        self.execution_history.append(history_entry)

    def killProcess(self):
        self.current_task = None

    def return_cpu_history(self):
        return self.execution_history

    def print_history(self):
        # Crear un DataFrame de pandas a partir de la lista de diccionarios
        df = pd.DataFrame(self.execution_history)

        # Imprimir la tabla usando tabulate con estilo "grid"
        self.logger.info(f"CPU Log:\n{tabulate(df, headers='keys', tablefmt='grid')}")

    
