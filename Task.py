from datetime import  date
from threading import  Thread
import time

class Task(Thread):
    last_date = 0
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        current_date = date.today()
        time.sleep(60)

