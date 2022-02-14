import os
from re import S
import pytest
from grader_service.registry import HandlerPathRegistry
from grader_service.server import GraderServer
from tornado_sqlalchemy import SQLAlchemy
from alembic.config import Config
from alembic.command import upgrade
from .db_util import insert_assignments
import tornado
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="module")
def db_test_config():
    cfg = Config(
        os.path.abspath(os.path.dirname(__file__) + "../../../alembic_test.ini")
    )
    cfg.set_main_option("script_location", os.path.abspath(os.path.dirname(__file__) + "../../../alembic"))
    yield cfg

@pytest.fixture(scope="function")
def sql_alchemy_db(db_test_config):
    db = SQLAlchemy(url="sqlite:///:memory:")
    engine = db.engine
    with engine.begin() as connection:
        db_test_config.attributes["connection"] = connection
        # downgrade(cfg, "base")
        upgrade(db_test_config, "head")
    engine = db.engine
    insert_assignments(engine)
    yield db


@pytest.fixture(scope="function")
def app(tmpdir, sql_alchemy_db):
    service_dir = str(tmpdir.mkdir("grader_service"))
    handlers = HandlerPathRegistry.handler_list()
    GraderServer.hub_service_name = ""
    GraderServer.hub_api_token = ""
    GraderServer.hub_api_url = ""
    GraderServer.hub_base_url = ""
    GraderServer.hub_service_prefix = ""
    GraderServer.hub_service_url = ""
    application = GraderServer(
        grader_service_dir=service_dir,
        handlers=handlers,
        db=sql_alchemy_db,
        cookie_secret="test",
    )
    yield application


@pytest.fixture(scope="module")
def service_base_url():
    base_url = "/services/grader"
    yield base_url


@pytest.fixture(scope="function")
def jupyter_hub_mock_server(httpserver):
    def for_user(login_user: dict, token: str):
        httpserver.expect_request(f"/authorizations/token/{token}").respond_with_json(
            login_user
        )
        return httpserver

    yield for_user

@pytest.fixture(scope="function")
def default_user():
    user = {
        "kind": "user",
        "name": "ubuntu",
        "admin": False,
        "groups": ["20wle2__instructor", "21wle1__student", "22wle1__instructor"],
    }
    yield user

@pytest.fixture(scope="function")
def default_token():
    token = "some_token"
    yield token
