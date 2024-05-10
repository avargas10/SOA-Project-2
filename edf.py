
from scheduler import Scheduler, ExecutableItems

class EarliestDeadlineFirstScheduler(Scheduler):
    def run(self):
        if self.aperiodic:
            self.runAperiodic()
        else:
            self.runPeriodic()

    def validateNewTasks(self, task):
        if task.startedTime == self.current_time:
            if not self.isExecuting(task) and task.aperiodic:
                self.execution_queue.append({ExecutableItems.pid.value: task.pid, 
                                         ExecutableItems.period.value: task.period, 
                                         ExecutableItems.deadline.value: task.deadline + task.startedTime, 
                                         ExecutableItems.startTime.value: task.startedTime})
                self.execution_queue.sort(key=lambda executable: executable[ExecutableItems.deadline.value])
    
    def isExecuting(self, task):
        isExec = False
        if task.started:
            for executable in self.execution_queue:
                executable[ExecutableItems.pid.value] == task.pid
                isExec = True
        return isExec


    def runAperiodic(self):
        self.tasks.sort(key=lambda task: task.deadline + task.startedTime)  # RMS: Ordena por periodo (menor a mayor)
        self.assign_priorities()
        for self.current_time in range(self.simulation_time):
            for task in self.tasks:
                self.validateNewTasks(task)
            executed = False
            count_executables = len(self.execution_queue)
            self.evaluateEmptyRun(-1, executed, count_executables)
            for index, task_pid in enumerate(self.execution_queue):
                # self.logger.info(f"self.execution_queue {self.execution_queue}")
                # self.logger.info(f"Analyzing {task_pid} at {self.current_time}")
                if not self.is_deadline_met(task_pid) and not executed:
                    task, task_finished, executed = self.send_task_to_cpu(task_pid)
                    if task_finished:
                        self.logger.info(f"Task {task.pid} finished at {self.current_time}")
                        self.removeExecutable(task.pid)
                    self.updateTask(task)
                else:
                    self.evaluateEmptyRun(index, executed, count_executables)
        self.cpu.print_history()
        self.save_statistics()

    def runPeriodic(self):
        self.tasks.sort(key=lambda task: task.deadline)  # RMS: Ordena por periodo (menor a mayor)
        self.assign_priorities()

        for self.current_time in range(self.simulation_time):
            for task in self.tasks:
                self.periodTriggered(task, ExecutableItems.deadline)
            executed = False
            count_executables = len(self.execution_queue)
            self.evaluateEmptyRun(-1, executed, count_executables)
            for index, task_pid in enumerate(self.execution_queue):
                # self.logger.info(f"self.execution_queue {self.execution_queue}")
                # self.logger.info(f"Analyzing {task_pid} at {self.current_time}")
                if not self.is_deadline_met(task_pid) and not executed:
                    task, task_finished, executed = self.send_task_to_cpu(task_pid)
                    if task_finished:
                        self.logger.info(f"Task {task.pid} finished at {self.current_time}")
                        self.removeExecutable(task.pid)
                    self.updateTask(task)
                else:
                    self.evaluateEmptyRun(index, executed, count_executables)
        self.cpu.print_history()
        self.save_statistics()