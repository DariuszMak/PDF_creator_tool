import pytest


@pytest.fixture()
def created_user_details(client):
    user = "test_user_created_details"
    password = "test_password"
    client.post(
        "/register",
        json={
            "name": user,
            "surname": "User's surname details",
            "email": "example_email@mail.com",
            "password": password,
        },
    )

    return user, password


@pytest.fixture()
def created_user_jwt(client, created_user_details):
    name, password = created_user_details
    response = client.post(
        "/login",
        json={"name": name, "password": password},
    )

    return response.json["access_token"]


def test_register_user(client, created_company_id):
    user = "test_user"
    response = client.post(
        "/register",
        json={
            "name": user,
            "surname": "User's surname details",
            "email": "example_email@mail.com",
            "password": "test_password",
        },
    )

    assert response.status_code == 201
    assert response.json == {"message": "User created successfully."}


def test_register_user_already_exists(client):
    user = "test_user"
    client.post(
        "/register",
        json={"name": user,
              "surname": "User's surname details",
              "email": "example_email@mail.com",
              "password": "test_password", },
    )

    response = client.post(
        "/register",
        json={"name": user,
              "surname": "User's surname details",
              "email": "example_email@mail.com",
              "password": "test_password", },
    )

    assert response.status_code == 409
    assert response.json["message"] == "A user with that user already exists."


def test_register_user_missing_data(client):
    response = client.post(
        "/register",
        json={},
    )

    assert response.status_code == 422
    assert "password" in response.json["errors"]["json"]
    assert "name" in response.json["errors"]["json"]


def test_login_user(client, created_user_details):
    name, password = created_user_details
    response = client.post(
        "/login",
        json={
            "name": name,
            "password": password,
        },
    )

    assert response.status_code == 200
    assert response.json["access_token"]


def test_login_user_incorrect_password(client, created_user_details):
    name, _ = created_user_details
    response = client.post(
        "/login",
        json={
            "name": name,
            "password": 'incorrect_password',
        },
    )

    assert response.status_code == 401
    assert response.json["message"] == "Invalid credentials."


def test_login_user_incorrect_name(client, created_user_details):
    _, password = created_user_details
    response = client.post(
        "/login",
        json={
            "name": "incorrect_name",
            "password": password,
        },
    )

    assert response.status_code == 401
    assert response.json["message"] == "Invalid credentials."


def test_get_user_register_details(client, jwt, created_user_details):
    response = client.get(
        "/user/1",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert response.json == {
        "company": None,
        "email": "example_email@mail.com",
        "id": 1,
        "name": "test_user_created_details",
        "surname": "User's surname details"
    }


def test_get_user_details_missing(client, jwt):
    response = client.get(
        "/user/23",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 404
    assert response.json == {"code": 404, "status": "Not Found"}


def test_create_user_in_company(client, jwt, created_company_id):
    response = client.post(
        "/user",
        json={"name": "User's name",
              "surname": "User's surname",
              "email": "example_email@mail.com",
              "password": "Password",
              "company_id": created_company_id},
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 201
    assert response.json["name"] == "User's name"
    assert response.json["surname"] == "User's surname"
    assert response.json["email"] == "example_email@mail.com"
    assert response.json["company"] == {"id": created_company_id, "name": "Test Company created in fixture"}


def test_create_user_with_company_id_not_found(client, jwt):
    response = client.post(
        "/user",
        json={"name": "User's name",
              "surname": "User's surname",
              "email": "example_email@mail.com",
              "password": "Password",
              "company_id": 1},
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 201
    assert response.json["name"] == "User's name"
    assert response.json["surname"] == "User's surname"
    assert response.json["email"] == "example_email@mail.com"
    assert response.json["company"] is None


def test_create_user_with_unknown_data(client, jwt):
    response = client.post(
        "/user",
        json={
            "name": "User's name",
            "surname": "User's surname",
            "email": "example_email@mail.com",
            "password": "Password",
            "company_id": 1,
            "unknown_field": "unknown",
        },
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 422
    assert response.json["errors"]["json"]["unknown_field"] == ["Unknown field."]


def test_delete_user(client, jwt, created_user_id):
    response = client.delete(
        f"/user/{created_user_id}",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert response.json["message"] == "User deleted."


def test_assign_user_to_company_that_is_not_associated(client, jwt):
    company_response = client.post(
        "/company",
        json={"name": "Test Company"},
        headers={"Authorization": f"Bearer {jwt}"}
    )

    created_company_id = company_response.json["id"]

    user_response = client.post(
        "/user",
        json={
            "name": "User's name",
            "surname": "User's surname",
            "email": "example_email@mail.com",
            "password": "example_password",
            "company_id": created_company_id + 1
        },
        headers={"Authorization": f"Bearer {jwt}"},
    )

    created_user_id = user_response.json["id"]

    response = client.put(
        f"/user/{created_user_id}",
        json={
            "name": "User's name renamed",
            "surname": "User's surname renamed",
            "email": "example_email@mail.com renamed",
            "password": "Password"
        },
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert response.json["name"] == "User's name renamed"
    assert response.json["surname"] == "User's surname renamed"
    assert response.json["email"] == "example_email@mail.com renamed"
    assert response.json["company"] is None


def test_assign_user_to_company_that_is_already_associated(client, jwt):
    company_response = client.post(
        "/company",
        json={"name": "Test Company"},
        headers={"Authorization": f"Bearer {jwt}"}
    )

    created_company_id = company_response.json["id"]

    user_response = client.post(
        "/user",
        json={
            "name": "User's name",
            "surname": "User's surname",
            "email": "example_email@mail.com",
            "password": "example_password",
            "company_id": created_company_id
        },
        headers={"Authorization": f"Bearer {jwt}"},
    )

    created_user_id = user_response.json["id"]

    response = client.put(
        f"/user/{created_user_id}",
        json={
            "name": "User's name renamed",
            "surname": "User's surname renamed",
            "email": "example_email@mail.com renamed",
            "password": "Password",
            "company_id": created_company_id,
        },
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 409
    assert response.json["message"] == "A user is already associated with a company."


def test_unassign_user_from_company_with_many_associated(client, jwt):
    company_response = client.post(
        "/company",
        json={"name": "Test Company"},
        headers={"Authorization": f"Bearer {jwt}"}
    )

    created_company_id = company_response.json["id"]

    second_company_response = client.post(
        "/company",
        json={"name": "Test Company 2"},
        headers={"Authorization": f"Bearer {jwt}"}
    )

    created_company_second_id = second_company_response.json["id"]

    third_company_response = client.post(
        "/company",
        json={"name": "Test Company 3"},
        headers={"Authorization": f"Bearer {jwt}"}
    )

    created_company_third_id = third_company_response.json["id"]

    user_response = client.post(
        "/user",
        json={
            "name": "User's name",
            "surname": "User's surname",
            "email": "example_email@mail.com",
            "password": "example_password",
            "company_id": created_company_id
        },
        headers={"Authorization": f"Bearer {jwt}"},
    )

    created_user_id = user_response.json["id"]

    user_second_response = client.post(
        "/user",
        json={
            "name": "User's name 2",
            "surname": "User's surname 2",
            "email": "example_email@mail.com2",
            "password": "example_password2",
            "company_id": created_company_second_id
        },
        headers={"Authorization": f"Bearer {jwt}"},
    )

    created_user_second_id = user_second_response.json["id"]

    response = client.put(
        f"/user/{created_user_id}",
        json={
            "name": "User's name renamed",
            "surname": "User's surname renamed",
            "email": "example_email@mail.com renamed",
            "password": "Password",
            "company_id": created_company_third_id,
        },
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200


def test_unassign_user_from_company_and_remove_company(client, jwt):
    company_response = client.post(
        "/company",
        json={"name": "Test Company"},
        headers={"Authorization": f"Bearer {jwt}"}
    )

    created_company_id = company_response.json["id"]

    second_company_response = client.post(
        "/company",
        json={"name": "Test Company 2"},
        headers={"Authorization": f"Bearer {jwt}"}
    )

    created_company_second_id = second_company_response.json["id"]

    third_company_response = client.post(
        "/company",
        json={"name": "Test Company 3"},
        headers={"Authorization": f"Bearer {jwt}"}
    )

    created_company_third_id = third_company_response.json["id"]

    user_response = client.post(
        "/user",
        json={
            "name": "User's name",
            "surname": "User's surname",
            "email": "example_email@mail.com",
            "password": "example_password",
            "company_id": created_company_id
        },
        headers={"Authorization": f"Bearer {jwt}"},
    )

    created_user_id = user_response.json["id"]

    response = client.put(
        f"/user/{created_user_id}",
        json={
            "name": "User's name renamed",
            "surname": "User's surname renamed",
            "email": "example_email@mail.com renamed",
            "password": "Password",
            "company_id": None,
        },
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200

    response_no_company = client.get(
        f"/company/{created_company_id}",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response_no_company.status_code == 404
    assert response_no_company.json == {"code": 404, "status": "Not Found"}


def test_get_all_users(client, jwt):
    response = client.post(
        "/company",
        json={"name": "Test Company"},
        headers={"Authorization": f"Bearer {jwt}"}
    )

    created_company_id = response.json["id"]

    client.post(
        "/user",
        json={"name": "User's name",
              "surname": "User's surname",
              "email": "example_email@mail.com",
              "password": "Password",
              "company_id": created_company_id},
        headers={"Authorization": f"Bearer {jwt}"},
    )

    client.post(
        "/user",
        json={"name": "User's name 2",
              "surname": "User's surname 2",
              "email": "example_email@mail.com",
              "password": "Password2",
              "company_id": created_company_id},
        headers={"Authorization": f"Bearer {jwt}"},
    )

    response = client.get(
        "/user",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json == [{'company': {'id': 1, 'name': 'Test Company'},
                              'email': 'example_email@mail.com',
                              'id': 1,
                              'name': "User's name",
                              'surname': "User's surname"},
                             {'company': {'id': 1, 'name': 'Test Company'},
                              'email': 'example_email@mail.com',
                              'id': 2,
                              'name': "User's name 2",
                              'surname': "User's surname 2"}]


def test_get_all_users_empty(client, jwt):
    response = client.get(
        "/user",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert len(response.json) == 0


def test_get_user_details(client, jwt, created_user_id, created_company_id):
    response = client.get(
        f"/user/{created_user_id}",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert response.json["name"] == "User's name created in fixture"
    assert response.json["surname"] == "User's surname created in fixture"
    assert response.json["email"] == "example_email@mail.com"
    assert response.json["company"] == {"id": created_company_id, "name": "Test Company created in fixture"}


def test_get_user_detail_not_found(client, jwt):
    response = client.get(
        "/user/1",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 404
    assert response.json == {"code": 404, "status": "Not Found"}
