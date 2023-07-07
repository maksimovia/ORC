from PyQt6.QtCore import QObject, QThread
import time


class Worker(QObject):

    def run(self):

        for i in range(999):
            print(i)
            time.sleep(0.5)


CYCLE = Worker()
CYCLE.run()