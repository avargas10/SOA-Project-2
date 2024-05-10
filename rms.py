from scheduler import Scheduler, ExecutableItems


class RateMonotonicScheduler(Scheduler):
    def calculate_utilization(self):
        utilization = sum(task.execution_time / task.period for task in self.tasks)
        return utilization
    

    def run(self):
        self.tasks.sort(key=lambda task: task.period)  # RMS: Ordena por periodo (menor a mayor)
        self.assign_priorities()

        for self.current_time in range(self.simulation_time):
            for task in self.tasks:
                self.periodTriggered(task, ExecutableItems.period)
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
        
            