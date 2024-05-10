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
    delete = "delete"


class Statistic(Enum):
    missed_deadlines = "missed_deadlines"
    executed_periods = "executed_periods"
    non_executed_periods = "non_executed_periods"
    missed_deadlines_percentage = "missed_deadlines_percentage"
    executed_periods_percentage = "executed_periods_percentage"
    non_executed_periods_percentage = "non_executed_periods_percentage"

class Scheduler:
    def __init__(self, simulation_time, name, cpu, aperiodic=False, randomGenerator=False):
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
        if self.aperiodic:
            task.aperiodic = self.aperiodic
            task.updatedStartedTime(task.period)
            if self.randomGenerator:
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

    def garbageCollector(self):
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
        for index, executable in enumerate(self.execution_queue):
            if executable[ExecutableItems.pid.value] == task_pid:
                if isLogicDelete:
                    self.logger.info(f"Disable {executable[ExecutableItems.pid.value]} from execution queue")
                    executable[ExecutableItems.delete.value] = True
                    self.execution_queue[index] = executable
                

    def removeExecutable(self, task_pid):
        self.logger.error(f"**** task_pid {task_pid}")
        id_list = [item[ExecutableItems.pid.value] for item in self.execution_queue]
        if task_pid in id_list:
            self.remove_from_execution_queue(task_pid, isLogicDelete=True)

    def is_deadline_met(self, task_pid):
        task = self.getTask(task_pid)
        deadline_met = False
        if self.current_time - task.startedTime >= task_pid[ExecutableItems.deadline.value]:
            deadline_met = True
            self.removeExecutable(task_pid[ExecutableItems.pid.value])
            self.cpu.killProcess(task_pid[ExecutableItems.pid.value])
            self.logger.warning(f"Deadline of task {task_pid[ExecutableItems.pid.value]} met at {self.current_time}")
            self.update_statistics(task, Statistic.missed_deadlines)
        return deadline_met
    
    def periodTriggered(self, task, key):
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
        for task in self.tasks:
            if task.pid == modified_task.pid:
                task = modified_task
    
    def evaluateEmptyRun(self, index, executed, count_executables):
        if len(self.execution_queue) == 0:
            self.logger.info(f"Empty run due to empty queue at {self.current_time}")
            return self.cpu.empty_run(self.current_time)
        elif index != -1 and index == count_executables - 1 and not executed:
            self.logger.info(f"Empty run due to last element at {self.current_time}")
            return self.cpu.empty_run(self.current_time)
                        


