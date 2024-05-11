import heapq
import time
from tabulate import tabulate
from cpu import CPU
from logger import Logger
from enum import Enum
import random
from constants import SCHEDULER_LOGGER, GENERAL_STATISTICS

class ExecutableItems(Enum):
    pid = "pid"  # Process ID
    period = "period"  # Period of the task
    deadline = "deadline"  # Deadline of the task
    startTime = "startTime"  # Start time of the task
    delete = "delete"  # Flag to mark if the task should be deleted from execution queue

class Statistic(Enum):
    missed_deadlines = "Missed Deadlines"  # Number of missed deadlines
    executed_periods = "Executed Periods"  # Number of executed periods
    non_executed_periods = "Non executed Periods"  # Number of non-executed periods
    missed_deadlines_percentage = "Missed Deadlines Percentage"  # Percentage of missed deadlines
    executed_periods_percentage = "Executed Periods Percentage"  # Percentage of executed periods
    non_executed_periods_percentage = "Non executed Periods Percentage"  # Percentage of non-executed periods

class Scheduler:
    def __init__(self, simulation_time, name, cpu, aperiodic=False, randomGenerator=False):
        """
        Initializes the scheduler with simulation parameters and configurations.
        
        Parameters:
        - simulation_time (int): Total simulation time.
        - name (str): Name of the scheduler.
        - cpu (CPU): CPU object for task execution.
        - aperiodic (bool): Flag indicating if the scheduler supports aperiodic tasks.
        - randomGenerator (bool): Flag indicating if random time generation is enabled.
        """
        self.simulation_time = simulation_time
        self.tasks = []
        self.name = name
        self.current_time = 0
        self.cpu = cpu
        self.statistics = {}
        self.preemp = True
        self.randomGenerator = randomGenerator
        self.aperiodic = aperiodic
        self.execution_queue = []
        self.logPath = SCHEDULER_LOGGER + "-" + name
        self.logger = Logger(self.logPath) 
        self.statisticsLogger = Logger(self.logPath + "-statistics")
        self.statistics[GENERAL_STATISTICS] = {
            Statistic.missed_deadlines.value: 0,
            Statistic.executed_periods.value: 0,
            Statistic.non_executed_periods.value: self.simulation_time
        }
        
    def initialize_random_int(self):
        """
        Generate a random integer between 0 and the specified limit.
        
        Returns:
        - int: A random integer between 0 and `simulation_time`.
        """
        if self.simulation_time < 0:
            raise ValueError("Limit must be non-negative.")
        
        # Generate a random integer between 0 and simulation_time
        random_int = random.randint(0, self.simulation_time)
        
        return random_int

    def add_task(self, task):
        """
        Adds a task to the scheduler.
        
        Parameters:
        - task (Task): Task object to be added.
        """
        self.statistics[task.pid] = {
            Statistic.missed_deadlines.value: 0,
            Statistic.executed_periods.value: 0,
            Statistic.non_executed_periods.value: self.simulation_time
        }
        if self.aperiodic:
            task.aperiodic = self.aperiodic
            task.updatedStartedTime(task.period)
            if self.randomGenerator:
                task.updatedStartedTime(self.initialize_random_int())
        self.tasks.append(task)

    def update_statistics(self, task, statistic):
        """
        Updates the statistics based on task execution.
        
        Parameters:
        - task (Task): Task for which statistics are updated.
        - statistic (Statistic): Type of statistic to update.
        """
        self.statistics[task.pid][statistic.value] += 1
        self.statistics[GENERAL_STATISTICS][statistic.value] += 1
        if statistic == Statistic.executed_periods:
            self.statistics[task.pid][Statistic.non_executed_periods.value] -= 1
            self.statistics[GENERAL_STATISTICS][Statistic.non_executed_periods.value] -= 1
        self.calculate_statistics_percentage(task)

    def calculate_statistics_percentage(self, task):
        """
        Calculates the percentage values for statistics.
        
        Parameters:
        - task (Task): Task for which percentage values are calculated.
        """
        self.statistics[task.pid][Statistic.executed_periods_percentage.value] = self.calculate_percentage(self.statistics[task.pid][Statistic.executed_periods.value])
        self.statistics[GENERAL_STATISTICS][Statistic.executed_periods_percentage.value] = self.calculate_percentage(self.statistics[GENERAL_STATISTICS][Statistic.executed_periods.value])
        self.statistics[task.pid][Statistic.non_executed_periods_percentage.value] = self.calculate_percentage(self.statistics[task.pid][Statistic.non_executed_periods.value])
        self.statistics[GENERAL_STATISTICS][Statistic.non_executed_periods_percentage.value] = self.calculate_percentage(self.statistics[GENERAL_STATISTICS][Statistic.non_executed_periods.value])
        

    def calculate_percentage(self, value):
        """
        Calculates the percentage value.
        
        Parameters:
        - value (int): Value to calculate the percentage for.
        
        Returns:
        - float: Percentage value.
        """
        return value*100/self.simulation_time
        
    def save_statistics(self):
        """
        Saves the statistics to log files.
        """
        # Extract general statistics and remaining tasks
        general_stats = self.statistics.pop('GENERAL_STATISTICS')  # Save and remove 'GENERAL_STATISTICS'
        tasks = self.statistics.items()  # Get the rest of the tasks

        # Determine column widths based on the longest content in each column
        headers = ["Task"] + list(general_stats.keys())
        column_widths = [
            max(len(str(val)), len(header))
            for header, val in zip(headers, [str(task) for task, _ in tasks] + list(general_stats.values()))
        ]

        # Create horizontal border
        horizontal_border = "+-" + "-+-".join("-" * width for width in column_widths) + "-+"

        # Print the table header
        self.logger.info(horizontal_border)
        header_row = "| " + " | ".join(
            header.ljust(width) for header, width in zip(headers, column_widths)
        ) + " |"
        self.statisticsLogger.info(header_row)
        self.statisticsLogger.info(horizontal_border)

        # Print the data for tasks
        for task, stats in tasks:
            row = [task] + list(stats.values())
            row_str = "| " + " | ".join(
                str(val).ljust(width) for val, width in zip(row, column_widths)
            ) + " |"
            self.statisticsLogger.info(row_str)

        # Print general statistics at the end
        general_row = ["GENERAL_STATISTICS"] + list(general_stats.values())
        general_row_str = "| " + " | ".join(
            str(val).ljust(width) for val, width in zip(general_row, column_widths)
        ) + " |"
        self.statisticsLogger.info(horizontal_border)
        self.statisticsLogger.info(general_row_str)
        self.statisticsLogger.info(horizontal_border)

    def run(self):
        """
        Method that simulates the scheduling.
        """
        raise NotImplementedError("Scheduler subclass must implement the 'run' method")
    
    def assign_priorities(self):
        """
        Assigns priorities to tasks based on their order.
        """
        for index, task in enumerate(self.tasks):
            task.priority = index

    def get_statistics(self):
        """
        Gets the statistics of the simulation.
        
        Returns:
        - dict: Statistics dictionary.
        """
        return self.statistics
    
    def getTask(self, task_pid):
        """
        Retrieves a task based on its process ID.
        
        Parameters:
        - task_pid (str): Process ID of the task to retrieve.
        
        Returns:
        - Task: Task object corresponding to the process ID.
        """
        for task in self.tasks:
            if task.pid == task_pid[ExecutableItems.pid.value]:
                return task

    def garbageCollector(self):
        """
        Cleans up the execution queue by removing completed or expired tasks.
        """
        new_execution_queue = self.execution_queue.copy()
        for executable in self.execution_queue:
            if executable[ExecutableItems.delete.value] == True:
                self.logger.info(f"Removing {executable[ExecutableItems.pid.value]} from execution queue")
                task = self.getTask(executable)
                task.resetTask()
                self.updateTask(task)
                new_execution_queue.remove(executable)
        self.execution_queue = new_execution_queue.copy()

    def remove_from_execution_queue(self, task_pid, isLogicDelete=False):
        """
        Removes a task from the execution queue.
        
        Parameters:
        - task_pid (str): Process ID of the task to remove.
        - isLogicDelete (bool): Flag indicating if the task is logically deleted (default is False).
        """
        for index, executable in enumerate(self.execution_queue):
            if executable[ExecutableItems.pid.value] == task_pid:
                if isLogicDelete:
                    self.logger.info(f"Disable {executable[ExecutableItems.pid.value]} from execution queue")
                    executable[ExecutableItems.delete.value] = True
                    self.execution_queue[index] = executable
                

    def removeExecutable(self, task_pid):
        """
        Removes an executable task from the execution queue.
        
        Parameters:
        - task_pid (str): Process ID of the task to remove.
        """
        id_list = [item[ExecutableItems.pid.value] for item in self.execution_queue]
        if task_pid in id_list:
            self.remove_from_execution_queue(task_pid, isLogicDelete=True)

    def is_deadline_met(self, task_pid):
        """
        Checks if the deadline of a task is met.
        
        Parameters:
        - task_pid (str): Process ID of the task to check.
        
        Returns:
        - bool: True if the deadline is met, False otherwise.
        """
        task = self.getTask(task_pid)
        deadline_met = False
        self.logger.info(f"task.startedTime {task.startedTime} task.deadline {task.deadline}")
        if self.current_time - task.startedTime >= task.deadline:
            deadline_met = True
            self.removeExecutable(task_pid[ExecutableItems.pid.value])
            self.cpu.killProcess(task_pid[ExecutableItems.pid.value])
            self.logger.warning(f"Deadline of task {task_pid[ExecutableItems.pid.value]} met at {self.current_time}")
            self.update_statistics(task, Statistic.missed_deadlines)
        return deadline_met
    
    def periodTriggered(self, task, key):
        """
        Handles periodic triggering of tasks.
        
        Parameters:
        - task (Task): Task triggered periodically.
        - key (ExecutableItems): Key to sort execution queue.
        """
        if self.current_time % task.period == 0:
            id_list = [item[ExecutableItems.pid.value] for item in self.execution_queue]
            if task.pid in id_list:
                self.removeExecutable(task.pid)
                self.logger.warning(f"Reschedule of task {task.pid} met at {self.current_time}")
                self.update_statistics(task, Statistic.missed_deadlines)
            self.execution_queue.append({ExecutableItems.pid.value: task.pid, 
                                         ExecutableItems.period.value: task.period, 
                                         ExecutableItems.deadline.value: task.deadline + self.current_time, 
                                         ExecutableItems.startTime.value: self.current_time,
                                         ExecutableItems.delete.value: False})
            task.startedTime = self.current_time
            self.updateTask(task)
            self.logger.info(f"Task period met adding to execution queue {task.pid} at {self.current_time}")
            self.execution_queue.sort(key=lambda task: task[key.value])

        
    def send_task_to_cpu(self, task_pid):
        """
        Sends a task to the CPU for execution.
        
        Parameters:
        - task_pid (str): Process ID of the task to send.
        
        Returns:
        - Tuple[Task, bool, bool]: Tuple containing the new task, finished flag, and executed flag.
        """
        current_task = self.cpu.current_task
        new_task = self.getTask(task_pid)
        finished = False
        executed = False
        if not current_task and new_task:
            self.logger.info(f"CPU empty executing {new_task.pid} at {self.current_time}")
            self.update_statistics(new_task, Statistic.executed_periods)
            new_task, finished = self.cpu.run_task(new_task, self.current_time)
            executed = True
        elif self.preemp and new_task and current_task.pid != new_task.pid and current_task.priority > new_task.priority:
            self.logger.warning(f"Swtiching tasks executing {new_task.pid}  at {self.current_time}")
            self.update_statistics(new_task, Statistic.executed_periods)
            new_task, finished = self.cpu.run_task(new_task, self.current_time)
            executed = True
        elif new_task.pid == current_task.pid:
            self.logger.info(f"Executing {new_task.pid} again at {self.current_time}")
            self.update_statistics(new_task, Statistic.executed_periods)
            new_task, finished = self.cpu.run_task(new_task, self.current_time)
            executed = True
        return new_task, finished, executed

    
    def updateTask(self, modified_task):
        """
        Updates a task in the task list.
        
        Parameters:
        - modified_task (Task): Modified task to update in the task list.
        """
        for task in self.tasks:
            if task.pid == modified_task.pid:
                task = modified_task
    
    def evaluateEmptyRun(self, index, executed, count_executables):
        """
        Evaluates conditions for performing an empty run.
        
        Parameters:
        - index (int): Current index in the execution queue.
        - executed (bool): Flag indicating if a task has been executed.
        - count_executables (int): Total count of executables in the queue.
        
        Returns:
        - Tuple[Task, bool]: Tuple containing the task and finished flag.
        """
        if len(self.execution_queue) == 0:
            self.logger.info(f"Empty run due to empty queue at {self.current_time}")
            return self.cpu.empty_run(self.current_time)
        elif index != -1 and index == count_executables - 1 and not executed:
            self.logger.info(f"Empty run due to last element at {self.current_time}")
            return self.cpu.empty_run(self.current_time)
