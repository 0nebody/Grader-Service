from datetime import datetime
from re import sub
import secrets
import pytest
from service.server import GraderServer
import json
from service.api.models.user import User
from service.api.models.submission import Submission
from tornado.httpclient import HTTPClientError
from datetime import timezone
from .db_util import insert_submission
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from service.autograding.local import LocalAutogradeExecutor
from service.autograding.feedback import GenerateFeedbackExecutor

# Imports are important otherwise they will not be found
from .tornado_test_utils import *


async def test_auto_grading(
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

    l_id = 3 # default user is student
    a_id = 3

    url = service_base_url + f"/lectures/{l_id}/assignments/{a_id}/grading/1/auto"

    engine = sql_alchemy_db.engine
    insert_assignments(engine, l_id)
    insert_submission(engine, a_id, default_user["name"])

    with patch.object(LocalAutogradeExecutor, "start", return_value=None):
        response = await http_server_client.fetch(
            url, method="GET", headers={"Authorization": f"Token {default_token}"}
        )
        assert response.code == 200
        submission = Submission.from_dict(json.loads(response.body.decode()))
        assert submission.id == 1



async def test_feedback(
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

    l_id = 3 # default user is student
    a_id = 3

    url = service_base_url + f"/lectures/{l_id}/assignments/{a_id}/grading/1/feedback"

    engine = sql_alchemy_db.engine
    insert_assignments(engine, l_id)
    insert_submission(engine, a_id, default_user["name"])

    with patch.object(GenerateFeedbackExecutor, "start", return_value=None):
        response = await http_server_client.fetch(
            url, method="GET", headers={"Authorization": f"Token {default_token}"}
        )
        assert response.code == 200
        submission = Submission.from_dict(json.loads(response.body.decode()))
        assert submission.id == 1

