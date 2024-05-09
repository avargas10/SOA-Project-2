
from scheduler import Scheduler

class EarliestDeadlineFirstScheduler(Scheduler):
    def run(self):
        # Simulación usando Earliest Deadline First (EDF)
        self.tasks.sort(key=lambda task: task.deadline)  # Ordena tareas por deadline (menor a mayor)

        for self.current_time in range(self.simulation_time):
            for task in self.tasks:
                if self.current_time % task.period == 0:  # Checa si debe ejecutar la tarea
                    if task.execution_time + self.current_time <= task.deadline:
                        self.statistics[task.name]['executed_periods'] += 1
                        # Simular ejecución de la tarea
                    else:
                        self.statistics[task.name]['missed_deadlines'] += 1
            # Las tareas que no se ejecutaron pueden incrementar su contador aquí