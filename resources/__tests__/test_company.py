def test_get_company(client, jwt, created_company_id):
    response = client.get(
        f"/company/{created_company_id}",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert response.json == {
        "id": 1,
        "name": "Test Company created in fixture",
        "users": [],
    }


def test_get_company_not_found(client, jwt):
    response = client.get(
        "/company/1",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 404
    assert response.json == {"code": 404, "status": "Not Found"}


def test_get_company_with_user(client, jwt, created_company_id):
    client.post(
        "/user",
        json={
            "name": "User's name",
            "surname": "User's surname",
            "email": "example_email@mail.com",
            "password": "Password",
            "company_id": created_company_id},
        headers={"Authorization": f"Bearer {jwt}"},
    )

    response = client.get(
        f"/company/{created_company_id}",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert response.json["users"] == [{"email": "example_email@mail.com",
                                       "id": 1,
                                       "name": "User's name",
                                       "surname": "User's surname",
                                       }]


def test_create_company(client, jwt):
    response = client.post(
        "/company",
        json={"name": "Test Company"},
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 201
    assert response.json["name"] == "Test Company"


def test_create_company_with_users(client, jwt, created_company_id):
    client.post(
        "/user",
        json={"name": "User's name",
              "surname": "User's surname",
              "email": "example_email@mail.com",
              "password": "Password",
              "company_id": created_company_id},
        headers={"Authorization": f"Bearer {jwt}"},
    )

    # Get the company with id 1 and check the users contains the newly created user
    response = client.get(
        f"/company/{created_company_id}",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert response.json["users"] == [{"email": "example_email@mail.com",
                                       "id": 1,
                                       "name": "User's name",
                                       "surname": "User's surname"}]


def test_create_company_only_current_user_is_already_assigned_with_a_company(client, jwt, created_user_id):
    response = client.post(
        "/company",
        json={"name": "Test Company 2"},
        headers={"Authorization": f"Bearer {jwt}"},
    )
    assert response.status_code == 409
    assert response.json["message"] == "A user is already associated with a company."


def test_delete_company(client, jwt, created_company_id):
    response = client.delete(
        f"/company/{created_company_id}",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert response.json == {"message": "Company deleted"}


def test_delete_company_doesnt_exist(client, jwt):
    response = client.delete(
        "/company/1",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 404
    assert response.json == {"code": 404, "status": "Not Found"}


def test_get_company_list_empty(client, jwt):
    response = client.get(
        "/company",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert response.json == []


def test_get_company_list_single(client, jwt):
    client.post(
        "/company",
        json={"name": "Test Company"},
        headers={"Authorization": f"Bearer {jwt}"},
    )

    response = client.get(
        "/company",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert response.json == [{"id": 1, "name": "Test Company", "users": []}]


def test_get_company_list_multiple(client, jwt):
    client.post(
        "/company",
        json={"name": "Test Company"},
        headers={"Authorization": f"Bearer {jwt}"},

    )
    client.post(
        "/company",
        json={"name": "Test Company 2"},
        headers={"Authorization": f"Bearer {jwt}"},

    )

    response = client.get(
        "/company",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert response.json == [{"id": 1, "name": "Test Company", "users": []},
                             {"id": 2, "name": 'Test Company 2', "users": []}]


def test_get_company_list_with_users(client, jwt):
    client.post(
        "/company",
        json={"name": "Test Company"},
        headers={"Authorization": f"Bearer {jwt}"},
    )
    client.post(
        "/user",
        json={"name": "User's name",
              "surname": "User's surname",
              "email": "example_email@mail.com",
              "password": "Password",
              "company_id": 1},
        headers={"Authorization": f"Bearer {jwt}"},
    )

    client.post(
        "/user",
        json={"name": "User's name2",
              "surname": "User's surname2",
              "email": "example_email@mail.com2",
              "password": "Password2",
              "company_id": 1},
        headers={"Authorization": f"Bearer {jwt}"},
    )

    response = client.get(
        "/company",
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert response.status_code == 200
    assert response.json == [{'id': 1,
                              'name': 'Test Company',
                              'users': [{'email': 'example_email@mail.com',
                                         'id': 1,
                                         'name': "User's name",
                                         'surname': "User's surname"},
                                        {'email': 'example_email@mail.com2',
                                         'id': 2,
                                         'name': "User's name2",
                                         'surname': "User's surname2"}]}]


def test_create_company_duplicate_name(client, jwt):
    client.post(
        "/company",
        json={"name": "Test Company"},
        headers={"Authorization": f"Bearer {jwt}"},
    )

    response = client.post(
        "/company",
        json={"name": "Test Company"},
        headers={"Authorization": f"Bearer {jwt}"},
    )
    assert response.status_code == 400
    assert response.json["message"] == "A company with that name already exists."
