
from scheduler import Scheduler, ExecutableItems

class EarliestDeadlineFirstScheduler(Scheduler):
    def run(self, isAperiodic=False):
        if isAperiodic:
            self.runAperiodic()
        else:
            self.runPeriodic()

    def runAperiodic(self):
        self.tasks.sort(key=lambda task: task.deadline)  # RMS: Ordena por periodo (menor a mayor)
        self.assign_priorities()

        for self.current_time in range(self.simulation_time):
            for task in self.tasks:
                self.periodTriggered(task, ExecutableItems.deadline)
            if len(self.execution_queue) == 0:
                self.cpu.empty_run(self.current_time)
            for task_pid in self.execution_queue:
                if not self.is_deadline_met(task_pid):
                    task, task_finished = self.send_task_to_cpu(task_pid)
                    if task_finished:
                        self.logger.info(f"Task {task.pid} finished at {self.current_time}")
                        self.removeExecutable(task.pid)
                    self.updateTask(task)
                    break
                else:
                    self.cpu.empty_run(self.current_time)
        self.cpu.print_history()
        self.save_statistics()
    
    def runPeriodic(self):
        self.tasks.sort(key=lambda task: task.deadline)  # RMS: Ordena por periodo (menor a mayor)
        self.assign_priorities()

        for self.current_time in range(self.simulation_time):
            for task in self.tasks:
                self.periodTriggered(task, ExecutableItems.deadline)
            if len(self.execution_queue) == 0:
                self.cpu.empty_run(self.current_time)
            for task_pid in self.execution_queue:
                if not self.is_deadline_met(task_pid):
                    task, task_finished = self.send_task_to_cpu(task_pid)
                    if task_finished:
                        self.logger.info(f"Task {task.pid} finished at {self.current_time}")
                        self.removeExecutable(task.pid)
                    self.updateTask(task)
                    break
                else:
                    self.cpu.empty_run(self.current_time)
        self.cpu.print_history()
        self.save_statistics()