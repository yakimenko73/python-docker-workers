import queue
import threading
import time

from docker.errors import ContainerError
from loguru import logger

from app.db.models import Task
from . import utils


class WorkersManager:
    def __init__(self, num_of_workers=2):
        self._queue = queue.Queue()
        self._num_of_workers = num_of_workers

    def start(self) -> None:
        logger.info("Start task workers manager")
        self._start_workers()

        self._gather_pending_tasks()

    def _start_workers(self) -> None:
        logger.info(f"Starting {self._num_of_workers} workers.")

        for i in range(self._num_of_workers):
            worker = WorkerThread(self._queue)
            worker.start()

    def _gather_pending_tasks(self) -> None:
        while True:
            tasks = Task.find_pending_tasks()
            if tasks:
                [self._queue.put(task) for task in tasks]
            else:
                logger.info("No tasks found, sleeping for 3 seconds.")
                time.sleep(3)

            self._queue.join()


class WorkerThread(threading.Thread):
    def __init__(self, queue_: queue.Queue, daemon=True):
        super().__init__(daemon=daemon)
        self._queue = queue_

    def run(self) -> None:
        while True:
            item: Task = self._queue.get()
            self._run_task(item)
            self._queue.task_done()

    @staticmethod
    def _run_task(task: Task) -> None:
        logger.info(f"Processing task {task.id}")
        task.update(status=Task.Status.running).execute()

        try:
            result = utils.execute_task_in_container(task)
            task.set_finished_status(result.execution_time, result.logs)

            logger.info(f"Task: {task.id} finished | Output: {result.logs}")
        except ContainerError as ex:
            task.update(status=Task.Status.failed).execute()

            logger.warning(f"Task: {task.id} failed | Exception: {ex}")
