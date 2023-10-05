import uuid

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_healthcheck():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "Ok"
    }


def test_get_accounts():
    response = client.get("/accounts")
    assert response.status_code == 200


def test_account_crud():
    randomName = f'Lorem {uuid.uuid4().__str__()}'
    createResponse = client.post("/accounts", json={"name": randomName})
    assert createResponse.status_code == 201
    user = createResponse.json()
    assert user["name"] == randomName
    print(f'/accounts/{user["id"]}')
    response = client.get(f'/accounts/{user["id"]}')
    assert response.status_code == 200
    assert response.json() == user

    randomName = f'Lorem {uuid.uuid4().__str__()}'
    updateResponse = client.put(f'/accounts/{user["id"]}', json={"name": randomName})

    assert updateResponse.status_code == 202

    user["name"] = randomName
    response = client.get(f'/accounts/{user["id"]}')
    assert response.status_code == 200
    assert response.json() == user

    deleteResponse = client.delete(f'/accounts/{user["id"]}')

    assert deleteResponse.status_code == 202

    deleteResponse = client.delete(f'/accounts/{user["id"]}')

    assert deleteResponse.status_code == 404
