import pytest

from src import init_app, db

CREATE_TASK_REQUEST = {
    "data": {
        "attributes": {
            "title": "Test",
            "description": "Run hello world in ubuntu",
            "command": "echo hello world",
            "image": "ubuntu"
        }
    }
}


@pytest.fixture
def client():
    api_app = init_app()
    api_app.config['TESTING'] = True
    db.init(api_app.config['TESTING'])

    yield api_app.test_client()


def test_list_tasks(client):
    response = client.get('/tasks')

    assert response.status_code == 200
    assert response.json == {'data': []}


def test_get_task(client):
    task = client.post('/tasks', json=CREATE_TASK_REQUEST)
    response = client.get(f'/tasks/{task.json["data"]["id"]}')

    assert response.status_code == 200
    assert response.json["data"]["attributes"]["title"] == CREATE_TASK_REQUEST["data"]["attributes"]["title"]


def test_create_task(client):
    response = client.post('/tasks', json=CREATE_TASK_REQUEST)

    assert response.status_code == 201


def test_create_task_exceeded(client):
    [client.post('/tasks', json=CREATE_TASK_REQUEST) for _ in range(client.application.config['MAX_TASKS_COUNT'])]

    response = client.post('/tasks', json=CREATE_TASK_REQUEST)

    assert response.status_code == 400
    assert response.json["message"] == "Max tasks number exceeded"
