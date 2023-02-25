import enum

import peewee

from . import db


class Task(peewee.Model):
    class Meta:
        database = db

    class Status(str, enum.Enum):
        pending = 'pending'
        running = 'running'
        finished = 'finished'
        failed = 'failed'

    title = peewee.CharField(max_length=20, null=False)
    image = peewee.CharField(max_length=255, null=False)
    command = peewee.CharField(max_length=255, null=False)
    description = peewee.CharField(max_length=255, null=False)
    status = peewee.CharField(max_length=20, null=False, default=Status.pending.value)
    execution_time = peewee.IntegerField(null=True)
    logs = peewee.TextField(null=True)

    def __str__(self):
        return f"Task {self.id}: {self.title}"

    def to_response(self, base_url: str) -> dict:
        return {
            "id": self.id,
            "type": "tasks",
            "attributes": {
                "title": self.title,
                "status": self.status,
                "image": self.image,
                "command": self.command,
                "description": self.description,
                "execution-time": self.execution_time
            },
            "links": {
                "self": f"{base_url}/{self.id}",
                "logs": f"{base_url}/{self.id}/logs"
            },
        }

    def set_finished_status(self, execution_time: str, logs: str) -> None:
        self.update(
            execution_time=execution_time,
            status=Task.Status.finished,
            logs=logs,
        ).execute()

    @staticmethod
    def find_pending_tasks():
        return Task.select().where(Task.status == Task.Status.pending)
