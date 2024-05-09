from logger import Logger
from constants import TASK_LOGGER

class Task:
    def __init__(self, pid, period, execution_time, deadline):
        self.pid = pid
        self.period = period
        self.execution_time = execution_time
        self.deadline = deadline
        self.runHistory = []
        self.runningTime = 0
        self.started = False
        self.startedTime = 0
        self.priority = 0
        self.logPath = TASK_LOGGER + "-" + pid
        self.logger = Logger(self.logPath) 

    def resetTask(self):
        self.runningTime = 0
        self.startedTime = 0
        self.started = False

    def run(self, currentTime):
        finish = False
        if not self.started:
            self.started = True
            self.startedTime = currentTime
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
        return f"Task({self.pid}, period={self.period}, execution_time={self.execution_time}, deadline={self.deadline})"
