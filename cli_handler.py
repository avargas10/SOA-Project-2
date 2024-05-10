import argparse
import sys
from task import Task
from rms import RateMonotonicScheduler
from edf import EarliestDeadlineFirstScheduler
from file_manager import read_tasks_from_file, write_statistics_to_file
from cpu import CPU

def main():
    parser = argparse.ArgumentParser(description='Simulador de Scheduling de Tiempo Real')
    parser.add_argument('-i', '--input', type=str, required=True, help='Archivo de entrada con tareas')
    parser.add_argument('-o', '--output', type=str, required=True, help='Archivo de salida para estadísticas')
    parser.add_argument('-a', '--algorithm', type=str, required=True, choices=['RMS', 'EDF', 'EDFA'], help='Algoritmo de scheduling')
    parser.add_argument('-t', '--time', type=int, required=True, help='Tiempo de simulación')
    parser.add_argument('-r', '--random', type=bool, required=False, help='Random Init Times')

    args = parser.parse_args()
    aperiodic = False
    cpu = CPU("Processor")
    if args.algorithm == 'RMS':
        scheduler = RateMonotonicScheduler(args.time, args.algorithm, cpu=cpu)
    elif args.algorithm == 'EDF':
        scheduler = EarliestDeadlineFirstScheduler(args.time, args.algorithm, cpu=cpu)
    elif args.algorithm == 'EDFA':
        scheduler = EarliestDeadlineFirstScheduler(args.time, args.algorithm, cpu=cpu, aperiodic=True, randomGenerator=args.random)
        aperiodic = True
    tasks = read_tasks_from_file(args.input, aperiodic=aperiodic)
    for task in tasks:
        scheduler.add_task(task)

    scheduler.run()

    statistics = scheduler.get_statistics()
    write_statistics_to_file(args.output, statistics)

if __name__ == '__main__':
    main()