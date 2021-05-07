from grader.common.models.assignment import Assignment
from grader.common.models.user import User
import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .db_util import *
from grader.service.persistence.database import DataBaseManager
from grader.service.persistence import assignment
import datetime


def test_get_assignments(full_db):
    setup_db_manager_mock(full_db)

    assign = assignment.get_assignments(1)
    assert len(assign) > 0

def test_get_assignment(full_db):
    setup_db_manager_mock(full_db)

    assign = assignment.get_assignment(1,1)
    assert assign.id == 1

def test_delete_assignment(full_db):
    setup_db_manager_mock(full_db)

    assign = assignment.get_assignments(1)
    before = len(assign)
    assignment.delete_assignment(Assignment(1,"assign1"))
    assign = assignment.get_assignments(1)
    after = len(assign)
    assert before > after

def test_update_assignment(full_db):
    setup_db_manager_mock(full_db)

    before = assignment.get_assignment(1,1)
    assignment.update_assignment(Assignment(id=1,name="newName",exercises=[],files=[],due_date=datetime.datetime.today(),status="created"))
    after = assignment.get_assignment(1,1)
    assert before.name != after.name


