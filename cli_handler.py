import argparse
import sys
from task import Task
from rms import RateMonotonicScheduler
from edf import EarliestDeadlineFirstScheduler
from file_manager import read_tasks_from_file, write_statistics_to_file
from cpu import CPU

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Real-Time Scheduling Simulator')

    # Add command-line arguments
    parser.add_argument('-i', '--input', type=str, required=True, help='Input file with tasks')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output file for statistics')
    parser.add_argument('-a', '--algorithm', type=str, required=True, choices=['RMS', 'EDF', 'EDFA'], help='Scheduling algorithm')
    parser.add_argument('-t', '--time', type=int, required=True, help='Simulation time')
    parser.add_argument('-r', '--random', type=bool, required=False, help='Random Init Times')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Initialize variables
    aperiodic = False
    cpu = CPU("Processor")

    # Choose the scheduler based on the selected algorithm
    if args.algorithm == 'RMS':
        scheduler = RateMonotonicScheduler(args.time, args.algorithm, cpu=cpu)
    elif args.algorithm == 'EDF':
        scheduler = EarliestDeadlineFirstScheduler(args.time, args.algorithm, cpu=cpu)
    elif args.algorithm == 'EDFA':
        scheduler = EarliestDeadlineFirstScheduler(args.time, args.algorithm, cpu=cpu, aperiodic=True, randomGenerator=args.random)
        aperiodic = True

    # Read tasks from the input file
    tasks = read_tasks_from_file(args.input, aperiodic=aperiodic)

    # Add tasks to the scheduler
    for task in tasks:
        scheduler.add_task(task)

    # Run the scheduler
    scheduler.run()

    # Get statistics from the scheduler
    statistics = scheduler.get_statistics()

    # Write statistics to the output file
    write_statistics_to_file(args.output, statistics)

if __name__ == '__main__':
    main()
