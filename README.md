# Real-Time Task Scheduler

## Overview

This project implements a real-time task scheduler capable of managing both periodic and aperiodic tasks efficiently. Real-time systems often require strict timing constraints, where tasks must be completed within specified deadlines. The scheduler ensures that tasks are executed in a timely manner according to their deadlines and priorities.

## Features

- **Scheduling Algorithms**: The scheduler supports various scheduling algorithms, including Rate Monotonic Scheduling (RMS) and Earliest Deadline First (EDF). These algorithms determine the order in which tasks are executed based on their characteristics such as period, execution time, and deadline.

- **Task Management**: Tasks are represented as objects with attributes such as PID (Process ID), period, execution time, and deadline. The scheduler can add tasks dynamically and manage their execution efficiently.

- **Logging**: The project includes logging functionality to track task execution, scheduler actions, and system statistics. Logs are saved to files for analysis and debugging purposes.

- **CPU Simulation**: A virtual CPU simulator is provided to execute tasks according to the scheduling algorithm. It maintains the current task and handles context switches between tasks.

## Components

The project consists of several modules:

- **scheduler.py**: Implements the main scheduler logic and provides implementations of scheduling algorithms such as RMS and EDF.

- **task.py**: Defines the `Task` class representing individual tasks in the system. Tasks have attributes such as period, execution time, and deadline.

- **cpu.py**: Contains the `CPU` class responsible for simulating task execution on a virtual CPU. It handles task execution and context switching.

- **logger.py**: Provides logging functionality for tracking task execution, scheduler actions, and system statistics.

- **constants.py**: Defines constants used throughout the project, including file paths for logging.

## Usage

To use the real-time task scheduler:

1. Define tasks using the `Task` class and specify their parameters such as period, execution time, and deadline.
2. Choose a scheduling algorithm (e.g., EDF or RMS) and create an instance of the corresponding scheduler class.
3. Add tasks to the scheduler using the `add_task` method.
4. Run the scheduler using the `run` method, which simulates task execution based on the chosen algorithm.

## Dependencies

- Python 3.x
- `tabulate` library (for tabular formatting)
- Other standard libraries such as `enum`, `heapq`, `time`, and `random`

## Author

This real-time task scheduler project was developed by [Your Name].

Feel free to contribute, provide feedback, or report issues!
