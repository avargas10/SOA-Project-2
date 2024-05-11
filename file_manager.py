from task import Task

def read_tasks_from_file(filename, aperiodic=False):
    """
    Reads tasks from a file and creates Task objects.

    Parameters:
    - filename (str): The name of the file containing task information.
    - aperiodic (bool): Indicates whether the tasks are aperiodic.

    Returns:
    - tasks (list): List of Task objects read from the file.
    """
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
    """
    Writes statistics to a file.

    Parameters:
    - filename (str): The name of the file to write statistics to.
    - statistics (dict): Dictionary containing task names as keys and their corresponding statistics as values.
    """
    with open(filename, 'w') as file:
        for task_name, stats in statistics.items():
            file.write(f"{task_name}: {stats}\n")
