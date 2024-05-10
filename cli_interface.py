from task import Task
from rms import RateMonotonicScheduler
from edf import EarliestDeadlineFirstScheduler
from scheduler import Scheduler

def cli():
    tasks = []  # This will store all tasks added by the user
    while True:
        print("\n1. Llamar a CLI command")
        print("2. Agregar tarea")
        print("3. Ejecutar scheduler")
        print("4. Ver tareas")
        print("5. Ver stadisticas")
        print("5. Salir")
        choice = input("Seleccione una opción: ")

        if choice == '2':
            id = input("Ingrese el ID de la tarea: ")
            periodo = int(input("Ingrese el período de la tarea: "))
            deadline = int(input("Ingrese el deadline de la tarea: "))
            tiempo_ejecucion = int(input("Ingrese el tiempo de ejecución de la tarea: "))
            tiempo_inicio = int(input("Ingrese el tiempo de inicio de la tarea: "))
            tarea = Task(id, periodo, deadline, tiempo_ejecucion, tiempo_inicio)
            tasks.append(tarea)
            print("Tarea agregada exitosamente.")
        elif choice == '3':
            if not tasks:
                print("No hay tareas agregadas para ejecutar.")
                continue
            print("Seleccione el tipo de Scheduler a ejecutar:")
            print("1. RMS")
            print("2. EDF")
            scheduler_choice = input("Ingrese su selección (1 para RMS, 2 para EDF): ")
            scheduler = Scheduler(mode='RMS' if scheduler_choice == '1' else 'EDF')
            for task in tasks:
                scheduler.agregar_tarea(task)
            scheduler.ejecutar()
            for log in scheduler.log:
                print(log)
            scheduler.log = []  # Clear the log after execution

        elif choice == '4':
            if not tasks:
                print("No hay tareas para mostrar.")
                continue
            print("\nListado de Tareas:")
            for task in tasks:
                print(f"\nID: {task.id}")
                print(f"Período: {'█' * task.periodo} ({task.periodo})")
                print(f"Deadline: {'█' * task.deadline} ({task.deadline})")
                print(f"Tiempo de Ejecución: {'█' * task.tiempo_ejecucion} ({task.tiempo_ejecucion})")
                print(f"Tiempo de Inicio: {task.tiempo_inicio}")
        elif choice == '5':
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
