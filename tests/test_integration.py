import json
import pytest

# Assert total Risk Percentages are hardcoded based on the following.
# base_risk = {
#     1: 10,  # After Hour Login
#     2: 20,  # Potential Account Sharing
#     3: 50,  # Terminated Employee Login
#     4: 15,  # Failed Attempt to Enter Building / Potential Tailgating
#     5: 50,  # Impossible Traveler
#     6: 50,  # Potential Data Exfiltration
# }
# If there is a change in the base risk in app.py, the test cases percentages would need to be recalculated and changed again.


def call(client, path, method="GET", body=None):
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}

    if method == "POST":
        response = client.post(path, data=json.dumps(body), headers=headers)
    elif method == "PUT":
        response = client.put(path, data=json.dumps(body), headers=headers)
    elif method == "PATCH":
        response = client.patch(path, data=json.dumps(body), headers=headers)
    elif method == "DELETE":
        response = client.delete(path)
    else:
        response = client.get(path)

    return {
        "json": json.loads(response.data.decode("utf-8")),
        "code": response.status_code,
    }


@pytest.mark.dependency()
def test_health(client):
    result = call(client, "health")
    assert result["code"] == 200


@pytest.mark.dependency(depends=["test_health"])
def test_percentage_no_logs(client):
    # Test data with empty lists for all categories
    test_data_empty = {"building_access": [], "proxy_log": [], "pc_access": []}

    # Testing with empty lists
    result_empty = call(client, "/percentage", method="POST", body=test_data_empty)
    assert (
        result_empty["code"] == 400
    ), "Expected 400 Bad Request for empty logs but got {}".format(result_empty["code"])

    expected_message = "No logs found in the request."
    assert (
        result_empty["json"]["message"] == expected_message
    ), "Unexpected message for empty logs"


@pytest.mark.dependency(depends=["test_health"])
def test_missing_keys(client):
    test_data = {
        "building_access": [
            {
                "suspect": 4,
            }
        ]
    }
    result = call(client, "/percentage", method="POST", body=test_data)

    assert result["code"] == 200
    assert "total_risk_percentage" in result["json"]

    expected_risk_percentage = 15
    assert result["json"]["total_risk_percentage"] == expected_risk_percentage


@pytest.mark.dependency(depends=["test_health"])
def test_missing_suspect_keys(client):
    test_data = {
        "building_access": [
            {
                "id": 28230,
                "user_id": 696,
                "access_date_time": "2023-01-15 03:43:14.000000",
                "direction": "OUT",
                "status": "FAIL",
                "office_location": "Beijing",
            }
        ]
    }
    result = call(client, "/percentage", method="POST", body=test_data)

    assert result["code"] == 400
    assert "Missing 'suspect' key" in result["json"]["message"], "Expected error message about missing 'suspect' key"



@pytest.mark.dependency(depends=["test_health"])
def test_missing_suspect_keys_multiple(client):
    test_data = {
        "building_access": [
            {
                "id": 28230,
                "user_id": 696,
                "access_date_time": "2023-01-15 03:43:14.000000",
                "direction": "OUT",
                "status": "FAIL",
                "office_location": "Beijing",
            },
            {
                "id": 29723,
                "user_id": 734,
                "access_date_time": "2023-01-04 04:28:37.000000",
                "direction": "IN",
                "status": "FAIL",
                "office_location": "Sydney",
                "suspect": 4,
            },
        ]
    }

    result = call(client, "/percentage", method="POST", body=test_data)

    assert result["code"] == 400
    assert "Missing 'suspect' key" in result["json"]["message"], "Expected error message about missing 'suspect' key"



@pytest.mark.dependency(depends=["test_health"])
def test_building_access_singular(client):
    test_data = {
        "building_access": [
            {
                "id": 28230,
                "user_id": 696,
                "access_date_time": "2023-01-15 03:43:14.000000",
                "direction": "OUT",
                "status": "FAIL",
                "office_location": "Beijing",
                "suspect": 4,
            }
        ]
    }

    result = call(client, "/percentage", method="POST", body=test_data)

    assert result["code"] == 200
    assert "total_risk_percentage" in result["json"]

    expected_risk_percentage = 15
    assert result["json"]["total_risk_percentage"] == expected_risk_percentage


@pytest.mark.dependency(depends=["test_health"])
def test_building_access_multiple(client):
    test_data = {
        "building_access": [
            {
                "id": 28230,
                "user_id": 696,
                "access_date_time": "2023-01-15 03:43:14.000000",
                "direction": "OUT",
                "status": "FAIL",
                "office_location": "Beijing",
                "suspect": 4,
            },
            {
                "id": 29723,
                "user_id": 734,
                "access_date_time": "2023-01-04 04:28:37.000000",
                "direction": "IN",
                "status": "FAIL",
                "office_location": "Sydney",
                "suspect": 4,
            },
        ]
    }

    result = call(client, "/percentage", method="POST", body=test_data)

    assert result["code"] == 200
    assert "total_risk_percentage" in result["json"]

    expected_risk_percentage = 23
    assert result["json"]["total_risk_percentage"] == expected_risk_percentage


@pytest.mark.dependency(depends=["test_health"])
def test_building_access_multiplev2(client):
    test_data = {
        "building_access": [
            {
                "id": 28230,
                "user_id": 696,
                "access_date_time": "2023-01-15 03:43:14.000000",
                "direction": "OUT",
                "status": "FAIL",
                "office_location": "Beijing",
                "suspect": 4,
            },
            {
                "id": 29723,
                "user_id": 734,
                "access_date_time": "2023-01-04 04:28:37.000000",
                "direction": "IN",
                "status": "FAIL",
                "office_location": "Sydney",
                "suspect": 4,
            },
            {
                "id": 32242,
                "user_id": 795,
                "access_date_time": "2023-01-17 00:24:58.000000",
                "direction": "IN",
                "status": "FAIL",
                "office_location": "New Jersey",
                "suspect": 4,
            },
        ]
    }

    result = call(client, "/percentage", method="POST", body=test_data)

    assert result["code"] == 200
    assert "total_risk_percentage" in result["json"]

    expected_risk_percentage = 27
    assert result["json"]["total_risk_percentage"] == expected_risk_percentage


@pytest.mark.dependency(depends=["test_health"])
def test_proxy_logs_singular(client):
    test_data = {
        "proxy_log": [
            {
                "id": 1349,
                "user_id": 12,
                "access_date_time": "2023-01-27 08:32:02.000000",
                "machine_name": "PC_12",
                "url": "https://resources.workable.com/tutorial/source-on-slack",
                "category": "Collaboration, Communication",
                "bytes_in": 3851864,
                "bytes_out": 87534786,
                "suspect": 6,
            }
        ]
    }

    result = call(client, "/percentage", method="POST", body=test_data)

    assert result["code"] == 200
    assert "total_risk_percentage" in result["json"]

    expected_risk_percentage = 50
    assert result["json"]["total_risk_percentage"] == expected_risk_percentage


@pytest.mark.dependency(depends=["test_health"])
def test_proxy_logs_multiple(client):
    test_data = {
        "proxy_log": [
            {
                "id": 1349,
                "user_id": 12,
                "access_date_time": "2023-01-27 08:32:02.000000",
                "machine_name": "PC_12",
                "url": "https://resources.workable.com/tutorial/source-on-slack",
                "category": "Collaboration, Communication",
                "bytes_in": 3851864,
                "bytes_out": 87534786,
                "suspect": 6,
            },
            {
                "id": 1402,
                "user_id": 13,
                "access_date_time": "2023-01-28 21:15:22.000000",
                "machine_name": "PC_13",
                "url": "https://www.pagseguro.uol.com.br",
                "category": "Finance",
                "bytes_in": 3773548,
                "bytes_out": 867207134,
                "suspect": 6,
            },
        ]
    }

    result = call(client, "/percentage", method="POST", body=test_data)

    assert result["code"] == 200
    assert "total_risk_percentage" in result["json"]

    expected_risk_percentage = 75
    assert result["json"]["total_risk_percentage"] == expected_risk_percentage


@pytest.mark.dependency(depends=["test_health"])
def test_pc_access_singular(client):
    test_data = {
        "pc_access": [
            {
                "id": 451,
                "user_id": 11,
                "access_date_time": "2023-01-05 01:42:50.000000",
                "log_on_off": "Log On",
                "machine_name": "PC_2146",
                "machine_location": "Sydney",
                "suspect": 5,
            }
        ]
    }

    result = call(client, "/percentage", method="POST", body=test_data)

    assert result["code"] == 200
    assert "total_risk_percentage" in result["json"]

    expected_risk_percentage = 50
    assert result["json"]["total_risk_percentage"] == expected_risk_percentage


@pytest.mark.dependency(depends=["test_health"])
def test_pc_access_multiple(client):
    test_data = {
        "pc_access": [
            {
                "id": 451,
                "user_id": 11,
                "access_date_time": "2023-01-05 01:42:50.000000",
                "log_on_off": "Log On",
                "machine_name": "PC_2146",
                "machine_location": "Sydney",
                "suspect": 5,
            },
            {
                "id": 2273,
                "user_id": 55,
                "access_date_time": "2023-01-08 16:28:54.000000",
                "log_on_off": "Log On",
                "machine_name": "PC_1972",
                "machine_location": "Tokyo",
                "suspect": 5,
            },
        ]
    }

    result = call(client, "/percentage", method="POST", body=test_data)

    assert result["code"] == 200
    assert "total_risk_percentage" in result["json"]

    expected_risk_percentage = 75
    assert result["json"]["total_risk_percentage"] == expected_risk_percentage


@pytest.mark.dependency(depends=["test_health"])
def test_combination_v1(client):
    test_data = {
        "pc_access": [
            {
                "id": 451,
                "user_id": 11,
                "access_date_time": "2023-01-05 01:42:50.000000",
                "log_on_off": "Log On",
                "machine_name": "PC_2146",
                "machine_location": "Sydney",
                "suspect": 5,
            },
            {
                "id": 2273,
                "user_id": 55,
                "access_date_time": "2023-01-08 16:28:54.000000",
                "log_on_off": "Log On",
                "machine_name": "PC_1972",
                "machine_location": "Tokyo",
                "suspect": 5,
            },
        ],
        "building_access": [
            {
                "id": 28230,
                "user_id": 696,
                "access_date_time": "2023-01-15 03:43:14.000000",
                "direction": "OUT",
                "status": "FAIL",
                "office_location": "Beijing",
                "suspect": 4,
            }
        ],
    }

    result = call(client, "/percentage", method="POST", body=test_data)

    assert result["code"] == 200
    assert "total_risk_percentage" in result["json"]

    expected_risk_percentage = 90
    assert result["json"]["total_risk_percentage"] == expected_risk_percentage


@pytest.mark.dependency(depends=["test_health"])
def test_combination_v2(client):
    test_data = {
        "pc_access": [
            {
                "id": 451,
                "user_id": 11,
                "access_date_time": "2023-01-05 01:42:50.000000",
                "log_on_off": "Log On",
                "machine_name": "PC_2146",
                "machine_location": "Sydney",
                "suspect": 1,
            },
            {
                "id": 2273,
                "user_id": 55,
                "access_date_time": "2023-01-08 16:28:54.000000",
                "log_on_off": "Log On",
                "machine_name": "PC_1972",
                "machine_location": "Tokyo",
                "suspect": 1,
            },
        ],
        "building_access": [
            {
                "id": 28230,
                "user_id": 696,
                "access_date_time": "2023-01-15 03:43:14.000000",
                "direction": "OUT",
                "status": "FAIL",
                "office_location": "Beijing",
                "suspect": 4,
            }
        ],
        "proxy_log": [
            {
                "id": 1349,
                "user_id": 12,
                "access_date_time": "2023-01-27 08:32:02.000000",
                "machine_name": "PC_12",
                "url": "https://resources.workable.com/tutorial/source-on-slack",
                "category": "Collaboration, Communication",
                "bytes_in": 3851864,
                "bytes_out": 87534786,
                "suspect": 6,
            }
        ],
    }

    result = call(client, "/percentage", method="POST", body=test_data)

    assert result["code"] == 200
    assert "total_risk_percentage" in result["json"]

    expected_risk_percentage = 80
    assert result["json"]["total_risk_percentage"] == expected_risk_percentage
