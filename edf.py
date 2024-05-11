from scheduler import Scheduler, ExecutableItems

class EarliestDeadlineFirstScheduler(Scheduler):
    def run(self):
        """
        Runs the scheduler based on whether it is aperiodic or periodic.
        """
        if self.aperiodic:
            self.runAperiodic()
        else:
            self.runPeriodic()

    def validateNewTasks(self, task):
        """
        Validates new tasks and adds them to the execution queue if they meet certain conditions.

        Parameters:
        - task (Task): The task to be validated.
        """
        if task.startedTime == self.current_time:
            if not self.isExecuting(task) and task.aperiodic:
                self.execution_queue.append({ExecutableItems.pid.value: task.pid, 
                                         ExecutableItems.period.value: task.period, 
                                         ExecutableItems.deadline.value: task.deadline + task.startedTime, 
                                         ExecutableItems.startTime.value: task.startedTime,
                                         ExecutableItems.delete.value: False})
                self.execution_queue.sort(key=lambda executable: executable[ExecutableItems.deadline.value])
    
    def isExecuting(self, task):
        """
        Checks if a task is currently executing.

        Parameters:
        - task (Task): The task to be checked.

        Returns:
        - isExec (bool): True if the task is executing, False otherwise.
        """
        isExec = False
        if task.started:
            for executable in self.execution_queue:
                executable[ExecutableItems.pid.value] == task.pid
                isExec = True
        return isExec

    def runAperiodic(self):
        """
        Runs the scheduler for aperiodic tasks.
        """
        self.tasks.sort(key=lambda task: task.deadline + task.startedTime)  # RMS: Ordena por periodo (menor a mayor)
        self.assign_priorities()
        for self.current_time in range(self.simulation_time):
            self.garbageCollector()
            for task in self.tasks:
                self.validateNewTasks(task)
            executed = False
            count_executables = len(self.execution_queue)
            self.evaluateEmptyRun(-1, executed, count_executables)
            for index, task_pid in enumerate(self.execution_queue):
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
        """
        Runs the scheduler for periodic tasks.
        """
        self.tasks.sort(key=lambda task: task.deadline)  # RMS: Ordena por periodo (menor a mayor)
        self.assign_priorities()

        for self.current_time in range(self.simulation_time):
            self.garbageCollector()
            for task in self.tasks:
                self.periodTriggered(task, ExecutableItems.deadline)
            executed = False
            count_executables = len(self.execution_queue)
            self.evaluateEmptyRun(-1, executed, count_executables)
            for index, task_pid in enumerate(self.execution_queue):
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
