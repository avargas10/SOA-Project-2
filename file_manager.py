from task import Task

def read_tasks_from_file(filename, aperiodic=False):
    tasks = []
    with open(filename, 'r') as file:
        for line in file:
            pid, period, execution_time, deadline = line.split(',')
            task = Task(pid=pid, 
                        period=int(period), 
                        execution_time=int(execution_time), 
                        deadline=int(deadline), 
                        aperiodic=aperiodic)
            tasks.append(task)
    return tasks

def write_statistics_to_file(filename, statistics):
    with open(filename, 'w') as file:
        for task_name, stats in statistics.items():
            file.write(f"{task_name}: {stats}\n")
