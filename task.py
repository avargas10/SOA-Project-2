from logger import Logger
from constants import TASK_LOGGER

class Task:
    def __init__(self, pid, period, execution_time, deadline, aperiodic=False):
        """
        Initializes a Task object with specified parameters.
        
        Parameters:
        - pid (str): Process ID of the task.
        - period (int): Period of the task.
        - execution_time (int): Execution time of the task.
        - deadline (int): Deadline of the task.
        - aperiodic (bool): Flag indicating if the task is aperiodic (default is False).
        """
        self.pid = pid
        self.period = period
        self.execution_time = execution_time
        self.deadline = deadline
        self.runHistory = []
        self.runningTime = 0
        self.started = False
        self.startedTime = 0
        self.aperiodic = aperiodic
        self.priority = 0
        self.logPath = TASK_LOGGER + "-" + pid
        self.logger = Logger(self.logPath) 
        self.logger.info(f"Task Created")
        self.reportCreation()

    def reportCreation(self):
        """
        Reports the creation details of the task.
        """
        self.logger.info(f"Task {self.pid} created")
        self.logger.info(f"\nPeriod {self.period}\nExecution Time {self.execution_time}\nDeadline {self.deadline}\nAperiodic {self.aperiodic}\nStarted Time {self.startedTime} ")

    def updatedStartedTime(self, startedTime):
        """
        Updates the started time of the task.
        
        Parameters:
        - startedTime (int): New started time of the task.
        """
        self.startedTime = startedTime
        self.logger.info(f"New StartedTime {self.startedTime}")

    def resetTask(self):
        """
        Resets the task attributes.
        """
        self.runningTime = 0
        self.startedTime = 0
        self.started = False

    def run(self, currentTime):
        """
        Simulates the execution of the task.
        
        Parameters:
        - currentTime (int): Current simulation time.
        
        Returns:
        - bool: True if the task finishes execution, False otherwise.
        """
        finish = False
        if not self.started:
            self.started = True
        self.runningTime += 1
        self.pendingTime = self.execution_time - self.runningTime
        self.logger.info({"Task": self.pid,
               "Finished": self.pendingTime == 0, 
               "Running Time": self.runningTime, 
               "Pending Time": self.pendingTime, 
               "Current Deadline": self.startedTime + self.deadline,
               "Current Time": currentTime})
        if(self.pendingTime == 0):
            self.runningTime = 0
            finish = True 
            self.startedTime = 0
            self.started = False
        return finish

    def __repr__(self):
        """
        Returns a string representation of the task.
        
        Returns:
        - str: String representation of the task.
        """
        return f"Task({self.pid}, period={self.period}, execution_time={self.execution_time}, deadline={self.deadline})"

