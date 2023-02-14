import pytest


@pytest.fixture()
def created_company_id(client, jwt):
    response = client.post(
        "/company",
        json={"name": "Test Company created in fixture"},
        headers={"Authorization": f"Bearer {jwt}"}
    )

    return response.json["id"]


@pytest.fixture()
def created_user_id(client, jwt, created_company_id):
    response = client.post(
        "/user",
        json={
            "name": "User's name created in fixture",
            "surname": "User's surname created in fixture",
            "email": "example_email@mail.com",
            "password": "example_password",
            "company_id": created_company_id
        },
        headers={"Authorization": f"Bearer {jwt}"},
    )

    return response.json["id"]
