from datetime import datetime

import pydantic

from app.db.models import Task
from . import client as DockerClient


class TaskExecutionResult(pydantic.BaseModel):
    execution_time: str
    logs: str


def execute_task_in_container(task: Task) -> TaskExecutionResult:
    start_time = datetime.now()
    container = DockerClient.containers.run(task.image, task.command, detach=True)
    end_time = datetime.now()
    logs = container.logs().decode('utf-8')

    container.remove(force=True)

    return TaskExecutionResult(
        execution_time=str(end_time - start_time),
        logs=logs
    )
