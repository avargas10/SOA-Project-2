import heapq
import time
from cpu import CPU
from logger import Logger
from enum import Enum
import random
from constants import SCHEDULER_LOGGER, GENERAL_STATISTICS

class ExecutableItems(Enum):
    pid = "pid"
    period = "period"
    deadline = "deadline"
    startTime = "startTime"


class Statistic(Enum):
    missed_deadlines = "missed_deadlines"
    executed_periods = "executed_periods"
    non_executed_periods = "non_executed_periods"
    missed_deadlines_percentage = "missed_deadlines_percentage"
    executed_periods_percentage = "executed_periods_percentage"
    non_executed_periods_percentage = "non_executed_periods_percentage"

class Scheduler:
    def __init__(self, simulation_time, name, cpu, aperiodic=False):
        self.simulation_time = simulation_time
        self.tasks = []
        self.name = name
        self.current_time = 0
        self.cpu = cpu
        self.statistics = {}
        self.preemp = True
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
        
        Parameters:
        - limit (int): The upper bound for the random integer. Must be greater than or equal to 0.
        
        Returns:
        - int: A random integer between 0 and `limit`.
        """
        if self.simulation_time < 0:
            raise ValueError("Limit must be non-negative.")
        
        # Generate a random integer between 0 and limit
        random_int = random.randint(0, self.simulation_time)
        
        return random_int

    def add_task(self, task):
        
        self.statistics[task.pid] = {
            Statistic.missed_deadlines.value: 0,
            Statistic.executed_periods.value: 0,
            Statistic.non_executed_periods.value: self.simulation_time
        }
        if task.aperiodic:
            task.updatedStartedTime(self.initialize_random_int())
        self.tasks.append(task)

    def update_statistics(self, task, statistic):
        self.statistics[task.pid][statistic.value] += 1
        self.statistics[GENERAL_STATISTICS][statistic.value] += 1
        if statistic == Statistic.executed_periods:
            self.statistics[task.pid][Statistic.non_executed_periods.value] -= 1
            self.statistics[GENERAL_STATISTICS][Statistic.non_executed_periods.value] -= 1
        self.calculate_statistics_percentage(task)

    def calculate_statistics_percentage(self, task):
        self.statistics[task.pid][Statistic.executed_periods_percentage.value] = self.calculate_percentage(self.statistics[task.pid][Statistic.executed_periods.value])
        self.statistics[GENERAL_STATISTICS][Statistic.executed_periods_percentage.value] = self.calculate_percentage(self.statistics[GENERAL_STATISTICS][Statistic.executed_periods.value])
        self.statistics[task.pid][Statistic.non_executed_periods_percentage.value] = self.calculate_percentage(self.statistics[task.pid][Statistic.non_executed_periods.value])
        self.statistics[GENERAL_STATISTICS][Statistic.non_executed_periods_percentage.value] = self.calculate_percentage(self.statistics[GENERAL_STATISTICS][Statistic.non_executed_periods.value])
        

    def calculate_percentage(self, value):
        return value*100/self.simulation_time
        

    def save_statistics(self):
        self.statisticsLogger.info(self.statistics)

    def run(self):
        # Método que simulará el scheduling
        raise NotImplementedError("Scheduler subclass must implement the 'run' method")
    
    def assign_priorities(self):
        for index, task in enumerate(self.tasks):
            task.priority = index

    def get_statistics(self):
        # Método para obtener estadísticas de la simulación
        return self.statistics
    
    def getTask(self, task_pid):
        for task in self.tasks:
            if task.pid == task_pid[ExecutableItems.pid.value]:
                return task

    def remove_from_execution_queue(self, task_pid):
        for executable in self.execution_queue:
            if executable[ExecutableItems.pid.value] == task_pid:
                task = self.getTask(executable)
                task.resetTask()
                self.updateTask(task)
                self.execution_queue.remove(executable)

    def removeExecutable(self, task_pid, aborted=False):
        id_list = [item[ExecutableItems.pid.value] for item in self.execution_queue]
        if task_pid in id_list:
            self.remove_from_execution_queue(task_pid)

    def is_deadline_met(self, task_pid):
        task = self.getTask(task_pid)
        deadline_met = False
        if self.current_time - task.startedTime >= task.deadline and task.started:
            deadline_met = True
            self.removeExecutable(task_pid, aborted=True)
            self.cpu.killProcess()
            self.logger.warning(f"Deadline of task {task_pid} met at {self.current_time}")
            self.update_statistics(task, Statistic.missed_deadlines)
        return deadline_met
    
    def periodTriggered(self, task, key):
        if self.current_time % task.period == 0:
            id_list = [item[ExecutableItems.pid.value] for item in self.execution_queue]
            if task.pid in id_list:
                self.removeExecutable(task.pid, aborted=True)
                self.logger.warning(f"Reschedule of task {task.pid} met at {self.current_time}")
                self.update_statistics(task, Statistic.missed_deadlines)
            self.execution_queue.append({ExecutableItems.pid.value: task.pid, 
                                         ExecutableItems.period.value: task.period, 
                                         ExecutableItems.deadline.value: task.deadline + self.current_time, 
                                         ExecutableItems.startTime.value: self.current_time})
            self.logger.info(f"Task period met adding to execution queue {task.pid} at {self.current_time}")
            self.execution_queue.sort(key=lambda task: task[key.value])

        
    def send_task_to_cpu(self, task_pid):
        current_task = self.cpu.current_task
        new_task = self.getTask(task_pid)
        if not current_task and new_task:
            current_task = new_task
            self.logger.info(f"CPU empty executing {current_task.pid} ")
        if self.preemp and new_task:
            if current_task.pid != new_task.pid and current_task.priority > new_task.priority:
                current_task = new_task
                self.logger.warning(f"Swtiching tasks executing {current_task.pid} ")
        self.update_statistics(current_task, Statistic.executed_periods)
        return self.cpu.run_task(current_task, self.current_time)

    
    def updateTask(self, modified_task):
        for task in self.tasks:
            if task.pid == modified_task.pid:
                task = modified_task
                        


