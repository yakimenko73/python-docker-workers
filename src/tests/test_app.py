import pytest

import app

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

# TODO: Retrieve from config or env vars
MAX_TASKS_COUNT = 100


@pytest.fixture
def client():
    """Fixture of slack app for client"""
    api_app = app.create_app()
    api_app.config['TESTING'] = True
    app.database.init_database(api_app.config['TESTING'])

    yield api_app.test_client()


def test_list_tasks(client):
    """Test listing task."""
    response = client.get('/tasks')

    assert response.status_code == 200
    assert response.json == {'data': []}


def test_get_task(client):
    """Test get a task."""
    task = client.post('/tasks', json=CREATE_TASK_REQUEST)
    response = client.get(f'/tasks/{task.json["data"]["id"]}')

    assert response.status_code == 200
    assert response.json["data"]["attributes"]["title"] == CREATE_TASK_REQUEST["data"]["attributes"]["title"]


def test_create_task(client):
    """Test creating a task."""
    response = client.post('/tasks', json=CREATE_TASK_REQUEST)

    assert response.status_code == 201


def test_create_task_exceeded(client):
    """Test creating a task."""
    [client.post('/tasks', json=CREATE_TASK_REQUEST) for _ in range(MAX_TASKS_COUNT)]

    response = client.post('/tasks', json=CREATE_TASK_REQUEST)

    assert response.status_code == 400
    assert response.json["message"] == "Max tasks number exceeded"
