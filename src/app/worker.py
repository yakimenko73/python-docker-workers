import queue
import threading
import time
from datetime import datetime

from loguru import logger

from .database import Task
from .docker.client import client as DockerClient


class Worker:
    def __init__(self, num_of_workers=2):
        self._queue = queue.Queue()
        self._num_of_workers = num_of_workers

    def start_workers(self):
        logger.info(f"Starting {self._num_of_workers} workers.")
        for i in range(self._num_of_workers):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()

    def worker(self):
        while True:
            item = self._queue.get()
            self._process_task(item)
            self._queue.task_done()

    def wait(self):
        """Wait for all tasks to be processed."""
        self._queue.join()

    def _put_task(self, task: Task):
        self._queue.put(task)

    @staticmethod
    def _process_task(task: Task):
        logger.info(f"Processing task {task.id}")
        task.update(status=Task.Status.running).execute()

        try:
            start_time = datetime.now()
            container = DockerClient.containers.run(task.image, task.command, detach=True)
            end_time = datetime.now()
            output = container.logs().decode('utf-8')

            task.set_finished_status(str(end_time - start_time), output)
            logger.info(f"Task: {task.id} finished | Output: {output}")
            container.remove()
        except Exception as ex:
            task.update(status=Task.Status.failed).execute()

            logger.info(f"Task: {task.id} failed | Exception: {ex}")

    def start(self):
        logger.info("Start task workers manager")
        self.start_workers()

        while True:
            tasks = Task.find_pending_tasks()
            if tasks:
                for task in tasks:
                    self._put_task(task)
            else:
                logger.info("No tasks found, sleeping for 3 seconds.")
                time.sleep(3)

            self.wait()
