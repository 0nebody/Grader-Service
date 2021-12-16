import pytest
from service.server import GraderServer
import json
from service.api.models.assignment import Assignment
from tornado.httpclient import HTTPClientError

# Imports are important otherwise they will not be found
from .db_util import insert_submission
from .tornado_test_utils import *


async def test_get_assignments(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/1/assignments/"

    response = await http_server_client.fetch(
        url, method="GET", headers={"Authorization": f"Token {default_token}"}
    )
    assert response.code == 200
    assignments = json.loads(response.body.decode())
    assert isinstance(assignments, list)
    assert len(assignments) > 0
    [Assignment.from_dict(l) for l in assignments]  # assert no errors


async def test_get_assignments_instructor(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
        sql_alchemy_db,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]

    l_id = 3 # default user is instructor
    url = service_base_url + f"/lectures/{l_id}/assignments/"

    engine = sql_alchemy_db.engine
    num_inserted = insert_assignments(engine, l_id)

    response = await http_server_client.fetch(
        url, method="GET", headers={"Authorization": f"Token {default_token}"}
    )
    assert response.code == 200
    assignments = json.loads(response.body.decode())
    assert isinstance(assignments, list)
    assert len(assignments) == num_inserted
    [Assignment.from_dict(l) for l in assignments]  # assert no errors


async def test_get_assignments_lecture_deleted(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
        sql_alchemy_db,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]

    l_id = 3  # default user is instructor

    # delete lecture
    url = service_base_url + f"/lectures/{l_id}/"
    delete_response = await http_server_client.fetch(
        url,
        method="DELETE",
        headers={"Authorization": f"Token {default_token}"},
    )
    assert delete_response.code == 200

    url = service_base_url + f"/lectures/{l_id}/assignments/"

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url, method="GET", headers={"Authorization": f"Token {default_token}"}
        )
    e = exc_info.value
    assert e.code == 404


async def test_post_assignment(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    get_response = await http_server_client.fetch(
        url, method="GET", headers={"Authorization": f"Token {default_token}"}
    )
    assert get_response.code == 200
    assignments = json.loads(get_response.body.decode())
    assert isinstance(assignments, list)
    orig_len = len(assignments)

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))
    assert post_assignment.id != pre_assignment.id
    assert post_assignment.name == pre_assignment.name
    assert post_assignment.type == pre_assignment.type
    assert post_assignment.status == pre_assignment.status
    assert post_assignment.due_date is None
    assert post_assignment.points == 0.0

    get_response = await http_server_client.fetch(
        url, method="GET", headers={"Authorization": f"Token {default_token}"}
    )
    assert get_response.code == 200
    assignments = json.loads(get_response.body.decode())
    assert len(assignments) == orig_len + 1


async def test_post_assignment_lecture_deleted(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]

    l_id = 3  # default user is instructor

    # delete lecture
    url = service_base_url + f"/lectures/{l_id}/"
    delete_response = await http_server_client.fetch(
        url,
        method="DELETE",
        headers={"Authorization": f"Token {default_token}"},
    )
    assert delete_response.code == 200

    url = service_base_url + "/lectures/3/assignments/"
    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="POST",
            headers={"Authorization": f"Token {default_token}"},
            body=json.dumps(pre_assignment.to_dict()),
        )
    e = exc_info.value
    assert e.code == 404


async def test_post_assignment_decode_error(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status=False, points=None)
    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="POST",
            headers={"Authorization": f"Token {default_token}"},
            body=json.dumps(pre_assignment.to_dict()),
        )
    e = exc_info.value
    assert e.code == 400

    pre_assignment = Assignment(id=-1, name="pytest", type=1, due_date=None, status="created", points=None)
    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="POST",
            headers={"Authorization": f"Token {default_token}"},
            body=json.dumps(pre_assignment.to_dict()),
        )
    e = exc_info.value
    assert e.code == 400


async def test_post_assignment_database_error(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]

    l_id = 3  # default user is instructor
    url = service_base_url + "/lectures/3/assignments/"

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="POST",
            headers={"Authorization": f"Token {default_token}"},
            body=json.dumps({"some": "value"}),
        )
    e = exc_info.value
    assert e.code == 400


async def test_post_no_status_error(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status=None, points=None)
    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="POST",
            headers={"Authorization": f"Token {default_token}"},
            body=json.dumps(pre_assignment.to_dict()),
        )
    e = exc_info.value
    assert e.code == 400


async def test_put_assignment(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    post_assignment.name = "new name"
    post_assignment.type = "group"
    post_assignment.status = "released"

    url = url + str(post_assignment.id)

    put_response = await http_server_client.fetch(
        url,
        method="PUT",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(post_assignment.to_dict()),
    )
    assert put_response.code == 200
    put_assignment = Assignment.from_dict(json.loads(put_response.body.decode()))
    assert put_assignment.id == post_assignment.id
    assert put_assignment.name == "new name"
    assert put_assignment.type == "group"
    assert put_assignment.status == "released"


async def test_put_assignment_wrong_lecture_id(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    # default user becomes instructor in lecture with id 1
    default_user["groups"] = ["20wle2__instructor", "21wle1__instructor", "22wle1__instructor"]
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    # now with lecture id 1
    url = service_base_url + "/lectures/1/assignments/" + str(post_assignment.id)

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="PUT",
            headers={"Authorization": f"Token {default_token}"},
            body=json.dumps(post_assignment.to_dict()),
        )
    e = exc_info.value
    assert e.code == 404


async def test_put_assignment_wrong_assignment_id(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    url = url + "99"
    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="PUT",
            headers={"Authorization": f"Token {default_token}"},
            body=json.dumps(post_assignment.to_dict()),
        )
    e = exc_info.value
    assert e.code == 404


async def test_put_assignment_deleted_assignment(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    url = url + str(post_assignment.id)

    delete_response = await http_server_client.fetch(
        url,
        method="DELETE",
        headers={"Authorization": f"Token {default_token}"},
    )
    assert delete_response.code == 200

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="PUT",
            headers={"Authorization": f"Token {default_token}"},
            body=json.dumps(post_assignment.to_dict()),
        )
    e = exc_info.value
    assert e.code == 404


async def test_put_assignment_no_point_changes(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    post_assignment.name = "new name"
    post_assignment.type = "group"
    post_assignment.status = "released"
    post_assignment.points = 10.0  # this has no effect

    url = url + str(post_assignment.id)

    put_response = await http_server_client.fetch(
        url,
        method="PUT",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(post_assignment.to_dict()),
    )
    assert put_response.code == 200
    put_assignment = Assignment.from_dict(json.loads(put_response.body.decode()))
    assert put_assignment.id == post_assignment.id
    assert put_assignment.name == "new name"
    assert put_assignment.type == "group"
    assert put_assignment.status == "released"
    assert put_assignment.points != 10.0


async def test_get_assignment(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    url = url + str(post_assignment.id)

    get_response = await http_server_client.fetch(
        url,
        method="GET",
        headers={"Authorization": f"Token {default_token}"},
    )
    assert get_response.code == 200
    get_assignment = Assignment.from_dict(json.loads(get_response.body.decode()))
    assert get_assignment.id == post_assignment.id
    assert get_assignment.name == post_assignment.name
    assert get_assignment.type == post_assignment.type
    assert get_assignment.status == post_assignment.status
    assert get_assignment.points == post_assignment.points
    assert get_assignment.due_date == post_assignment.due_date


async def test_get_assignment_created_student(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    l_id = 1  # default user is student
    a_id = 2  # assignment is created
    url = service_base_url + f"/lectures/{l_id}/assignments/{a_id}"

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="GET",
            headers={"Authorization": f"Token {default_token}"},
        )
    assert exc_info.value.code == 404


async def test_get_assignment_wrong_lecture_id(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    l_id = 3
    url = service_base_url + f"/lectures/{l_id}/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    l_id = 1
    url = service_base_url + f"/lectures/{l_id}/assignments/{post_assignment.id}"

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="GET",
            headers={"Authorization": f"Token {default_token}"},
        )
    assert exc_info.value.code == 404


async def test_get_assignment_wrong_assignment_id(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    l_id = 3
    url = service_base_url + f"/lectures/{l_id}/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200

    url = service_base_url + f"/lectures/{l_id}/assignments/99"

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="GET",
            headers={"Authorization": f"Token {default_token}"},
        )
    assert exc_info.value.code == 404


async def test_get_assignment_incorrect_param(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
        sql_alchemy_db,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]

    l_id = 3
    url = service_base_url + f"/lectures/{l_id}/assignments/3/?some_param=true"

    engine = sql_alchemy_db.engine
    insert_assignments(engine, 3)

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="GET",
            headers={"Authorization": f"Token {default_token}"},
        )
    e = exc_info.value
    assert e.code == 400


async def test_get_assignment_instructor_version(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
        sql_alchemy_db,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]

    l_id = 3
    url = service_base_url + f"/lectures/{l_id}/assignments/3/?instructor-version=true"

    engine = sql_alchemy_db.engine
    insert_assignments(engine, 3)

    get_response = await http_server_client.fetch(
        url,
        method="GET",
        headers={"Authorization": f"Token {default_token}"},
    )
    assert get_response.code == 200


async def test_get_assignment_instructor_version_unauthorized(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]

    l_id = 1
    a_id = 1
    url = service_base_url + f"/lectures/{l_id}/assignments/{a_id}/?instructor-version=true"

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="GET",
            headers={"Authorization": f"Token {default_token}"},
        )
    e = exc_info.value
    assert e.code == 403


async def test_delete_assignment(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    url = url + str(post_assignment.id)

    delete_response = await http_server_client.fetch(
        url,
        method="DELETE",
        headers={"Authorization": f"Token {default_token}"},
    )
    assert delete_response.code == 200

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="GET",
            headers={"Authorization": f"Token {default_token}"},
        )

    e = exc_info.value
    assert e.code == 404


async def test_delete_assignment_deleted_assignment(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    url = url + str(post_assignment.id)

    delete_response = await http_server_client.fetch(
        url,
        method="DELETE",
        headers={"Authorization": f"Token {default_token}"},
    )
    assert delete_response.code == 200

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="DELETE",
            headers={"Authorization": f"Token {default_token}"},
        )

    e = exc_info.value
    assert e.code == 404


async def test_delete_assignment_not_created(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/999"

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="DELETE",
            headers={"Authorization": f"Token {default_token}"},
        )
    e = exc_info.value
    assert e.code == 404


async def test_delete_assignment_with_submissions(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
        sql_alchemy_db
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]

    a_id = 1
    url = service_base_url + f"/lectures/3/assignments/{a_id}"

    engine = sql_alchemy_db.engine
    insert_submission(engine, assignment_id=a_id, username=default_user["name"])

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="DELETE",
            headers={"Authorization": f"Token {default_token}"},
        )
    e = exc_info.value
    assert e.code == 404


async def test_delete_assignment_same_name_twice(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    url = url + str(post_assignment.id)

    delete_response = await http_server_client.fetch(
        url,
        method="DELETE",
        headers={"Authorization": f"Token {default_token}"},
    )
    assert delete_response.code == 200

    url = service_base_url + "/lectures/3/assignments/"

    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    url = url + str(post_assignment.id)

    delete_response = await http_server_client.fetch(
        url,
        method="DELETE",
        headers={"Authorization": f"Token {default_token}"},
    )
    assert delete_response.code == 200


async def test_delete_released_assignment(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="released", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    url = url + str(post_assignment.id)

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="DELETE",
            headers={"Authorization": f"Token {default_token}"},
        )
    e = exc_info.value
    assert e.code == 400


async def test_delete_complete_assignment(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="complete", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    url = url + str(post_assignment.id)

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="DELETE",
            headers={"Authorization": f"Token {default_token}"},
        )
    e = exc_info.value
    assert e.code == 400


async def test_assignment_properties(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]
    url = service_base_url + "/lectures/3/assignments/"

    pre_assignment = Assignment(id=-1, name="pytest", type="user", due_date=None, status="created", points=None)
    post_response = await http_server_client.fetch(
        url,
        method="POST",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(pre_assignment.to_dict()),
    )
    assert post_response.code == 200
    post_assignment = Assignment.from_dict(json.loads(post_response.body.decode()))

    url = service_base_url + f"/lectures/3/assignments/{post_assignment.id}/properties"
    prop = {"test": "property", "value": 2, "bool": True, "null": None}
    put_response = await http_server_client.fetch(
        url,
        method="PUT",
        headers={"Authorization": f"Token {default_token}"},
        body=json.dumps(prop),
    )
    assert put_response.code == 200
    get_response = await http_server_client.fetch(
        url,
        method="GET",
        headers={"Authorization": f"Token {default_token}"},
    )
    assert get_response.code == 200
    assignment_props = json.loads(get_response.body.decode())
    assert assignment_props == prop


async def test_assignment_properties_lecture_assignment_missmatch(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
        sql_alchemy_db,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]

    l_id = 3
    a_id = 1
    engine = sql_alchemy_db.engine
    insert_assignments(engine, l_id)

    url = service_base_url + f"/lectures/{l_id}/assignments/{a_id}/properties"
    prop = {"test": "property", "value": 2, "bool": True, "null": None}

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="PUT",
            headers={"Authorization": f"Token {default_token}"},
            body=json.dumps(prop),
        )
    e = exc_info.value
    assert e.code == 404

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="GET",
            headers={"Authorization": f"Token {default_token}"},
        )
    e = exc_info.value
    assert e.code == 404


async def test_assignment_properties_wrong_assignment_id(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
        sql_alchemy_db,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]

    l_id = 3
    a_id = 99
    engine = sql_alchemy_db.engine
    insert_assignments(engine, l_id)

    url = service_base_url + f"/lectures/{l_id}/assignments/{a_id}/properties"
    prop = {"test": "property", "value": 2, "bool": True, "null": None}

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="PUT",
            headers={"Authorization": f"Token {default_token}"},
            body=json.dumps(prop),
        )
    e = exc_info.value
    assert e.code == 404

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="GET",
            headers={"Authorization": f"Token {default_token}"},
        )
    e = exc_info.value
    assert e.code == 404


async def test_assignment_properties_not_found(
        app: GraderServer,
        service_base_url,
        http_server_client,
        jupyter_hub_mock_server,
        default_user,
        default_token,
        sql_alchemy_db,
):
    http_server = jupyter_hub_mock_server(default_user, default_token)
    app.hub_api_url = http_server.url_for("")[0:-1]

    l_id = 3
    a_id = 3
    engine = sql_alchemy_db.engine
    insert_assignments(engine, l_id)

    url = service_base_url + f"/lectures/{l_id}/assignments/{a_id}/properties"

    with pytest.raises(HTTPClientError) as exc_info:
        await http_server_client.fetch(
            url,
            method="GET",
            headers={"Authorization": f"Token {default_token}"},
        )
    e = exc_info.value
    assert e.code == 404