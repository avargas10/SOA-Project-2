import pandas as pd
from datetime import datetime, timedelta
from tabulate import tabulate
from logger import Logger
from constants import CPU_LOGGER

class CPU:
    def __init__(self, name):
        """
        Initializes the CPU object with a name and sets initial attributes.

        Parameters:
        - name (str): The name of the CPU.
        """
        self.name = name
        self.current_task = None
        self.execution_history = []
        self.preemp = True
        self.logPath = CPU_LOGGER + "-" + name
        self.logger = Logger(self.logPath, clean=True) 

    def run_task(self, task, current_time):
        """
        Runs a task on the CPU.

        Parameters:
        - task (Task): The task to be executed.
        - current_time (datetime): The current time.

        Returns:
        - task (Task): The task being executed.
        - finished (bool): Whether the task has finished execution.
        """
        history_entry =  {"Task": task.pid , "Start": current_time, "Finish": current_time + 1}
        self.execution_history.append(history_entry)
        self.current_task = task
        finished = task.run(current_time)
        if finished:
            self.current_task = None
        return task, finished
    
    def empty_run(self, current_time):
        """
        Runs an empty cycle on the CPU (no task execution).

        Parameters:
        - current_time (datetime): The current time.
        """
        self.current_task = None
        history_entry =  {"Task": self.current_task , "Start": current_time, "Finish": current_time + 1}
        self.execution_history.append(history_entry)

    def killProcess(self, task_pid):
        """
        Kills a task currently running on the CPU if its PID matches the given PID.

        Parameters:
        - task_pid (int): The PID of the task to be killed.
        """
        if self.current_task and self.current_task.pid == task_pid:
            self.current_task = None

    def return_cpu_history(self):
        """
        Returns the execution history of the CPU.

        Returns:
        - execution_history (list): List of dictionaries representing CPU execution history.
        """
        return self.execution_history

    def print_history(self):
        """
        Prints the CPU execution history.
        """
        # Create a pandas DataFrame from the list of dictionaries
        df = pd.DataFrame(self.execution_history)

        # Print the table using tabulate with "grid" style
        self.logger.info(f"CPU Log:\n{tabulate(df, headers='keys', tablefmt='grid')}")
