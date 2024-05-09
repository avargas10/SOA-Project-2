from scheduler import Scheduler, Statistic


class RateMonotonicScheduler(Scheduler):
    def calculate_utilization(self):
        utilization = sum(task.execution_time / task.period for task in self.tasks)
        return utilization
    
    def is_schedulable(self):
        n = len(self.tasks)
        if n == 0:
            return True  # Sin tareas, siempre es planificable
        
        # Límite de Liu y Layland
        utilization_limit = n * (2**(1/n) - 1)
        
        total_utilization = self.calculate_utilization()
        
        return total_utilization <= utilization_limit

        # for task in self.tasks:
        #     print(f"Updated task {task.pid} with running {task.runningTime}")

    def run(self):
        if not self.is_schedulable():
            self.logger.error("Advertencia: El conjunto de tareas puede no ser planificable con Rate Monotonic Scheduling.")
        
        self.tasks.sort(key=lambda task: task.period)  # RMS: Ordena por periodo (menor a mayor)
        self.assign_priorities()

        for self.current_time in range(self.simulation_time):
            for task in self.tasks:
                self.periodTriggered(task)
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
        
            