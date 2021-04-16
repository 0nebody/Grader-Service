# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from common.models.base_model_ import Model
from common.models.assignment_file import AssignmentFile
from common.models.exercise import Exercise
from common import util

from common.models.assignment_file import AssignmentFile  # noqa: E501
from common.models.exercise import Exercise  # noqa: E501

class Assignment(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, name=None, exercises=None, files=None, due_date=None, status=None):  # noqa: E501
        """Assignment - a model defined in OpenAPI

        :param id: The id of this Assignment.  # noqa: E501
        :type id: int
        :param name: The name of this Assignment.  # noqa: E501
        :type name: str
        :param exercises: The exercises of this Assignment.  # noqa: E501
        :type exercises: List[Exercise]
        :param files: The files of this Assignment.  # noqa: E501
        :type files: List[AssignmentFile]
        :param due_date: The due_date of this Assignment.  # noqa: E501
        :type due_date: datetime
        :param status: The status of this Assignment.  # noqa: E501
        :type status: str
        """
        self.openapi_types = {
            'id': int,
            'name': str,
            'exercises': List[Exercise],
            'files': List[AssignmentFile],
            'due_date': datetime,
            'status': str
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'exercises': 'exercises',
            'files': 'files',
            'due_date': 'due_date',
            'status': 'status'
        }

        self._id = id
        self._name = name
        self._exercises = exercises
        self._files = files
        self._due_date = due_date
        self._status = status

    @classmethod
    def from_dict(cls, dikt) -> 'Assignment':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Assignment of this Assignment.  # noqa: E501
        :rtype: Assignment
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this Assignment.


        :return: The id of this Assignment.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Assignment.


        :param id: The id of this Assignment.
        :type id: int
        """

        self._id = id

    @property
    def name(self):
        """Gets the name of this Assignment.


        :return: The name of this Assignment.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Assignment.


        :param name: The name of this Assignment.
        :type name: str
        """

        self._name = name

    @property
    def exercises(self):
        """Gets the exercises of this Assignment.


        :return: The exercises of this Assignment.
        :rtype: List[Exercise]
        """
        return self._exercises

    @exercises.setter
    def exercises(self, exercises):
        """Sets the exercises of this Assignment.


        :param exercises: The exercises of this Assignment.
        :type exercises: List[Exercise]
        """

        self._exercises = exercises

    @property
    def files(self):
        """Gets the files of this Assignment.


        :return: The files of this Assignment.
        :rtype: List[AssignmentFile]
        """
        return self._files

    @files.setter
    def files(self, files):
        """Sets the files of this Assignment.


        :param files: The files of this Assignment.
        :type files: List[AssignmentFile]
        """

        self._files = files

    @property
    def due_date(self):
        """Gets the due_date of this Assignment.


        :return: The due_date of this Assignment.
        :rtype: datetime
        """
        return self._due_date

    @due_date.setter
    def due_date(self, due_date):
        """Sets the due_date of this Assignment.


        :param due_date: The due_date of this Assignment.
        :type due_date: datetime
        """

        self._due_date = due_date

    @property
    def status(self):
        """Gets the status of this Assignment.


        :return: The status of this Assignment.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this Assignment.


        :param status: The status of this Assignment.
        :type status: str
        """
        allowed_values = ["created", "released", "fetched", "complete"]  # noqa: E501
        if status not in allowed_values:
            raise ValueError(
                "Invalid value for `status` ({0}), must be one of {1}"
                .format(status, allowed_values)
            )

        self._status = status
