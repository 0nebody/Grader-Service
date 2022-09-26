# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from grader_labextension.api.models.base_model_ import Model
from grader_labextension.api import util


class Assignment(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, name=None, type=None, due_date=None, status=None, points=None, automatic_grading=None, max_submissions=None, allow_files=None):  # noqa: E501
        """Assignment - a model defined in OpenAPI

        :param id: The id of this Assignment.  # noqa: E501
        :type id: int
        :param name: The name of this Assignment.  # noqa: E501
        :type name: str
        :param type: The type of this Assignment.  # noqa: E501
        :type type: str
        :param due_date: The due_date of this Assignment.  # noqa: E501
        :type due_date: datetime
        :param status: The status of this Assignment.  # noqa: E501
        :type status: str
        :param points: The points of this Assignment.  # noqa: E501
        :type points: float
        :param automatic_grading: The automatic_grading of this Assignment.  # noqa: E501
        :type automatic_grading: str
        :param max_submissions: The max_submissions of this Assignment.  # noqa: E501
        :type max_submissions: int
        :param allow_files: The allow_files of this Assignment.  # noqa: E501
        :type allow_files: bool
        """
        self.openapi_types = {
            'id': int,
            'name': str,
            'type': str,
            'due_date': datetime,
            'status': str,
            'points': float,
            'automatic_grading': str,
            'max_submissions': int,
            'allow_files': bool
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'type': 'type',
            'due_date': 'due_date',
            'status': 'status',
            'points': 'points',
            'automatic_grading': 'automatic_grading',
            'max_submissions': 'max_submissions',
            'allow_files': 'allow_files'
        }

        self._id = id
        self._name = name
        self._type = type
        self._due_date = due_date
        self._status = status
        self._points = points
        self._automatic_grading = automatic_grading
        self._max_submissions = max_submissions
        self._allow_files = allow_files

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
    def type(self):
        """Gets the type of this Assignment.


        :return: The type of this Assignment.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Assignment.


        :param type: The type of this Assignment.
        :type type: str
        """
        allowed_values = ["user", "group"]  # noqa: E501
        if type not in allowed_values:
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"
                .format(type, allowed_values)
            )

        self._type = type

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
        allowed_values = ["created", "pushed", "released", "complete"]  # noqa: E501
        if status not in allowed_values:
            raise ValueError(
                "Invalid value for `status` ({0}), must be one of {1}"
                .format(status, allowed_values)
            )

        self._status = status

    @property
    def points(self):
        """Gets the points of this Assignment.


        :return: The points of this Assignment.
        :rtype: float
        """
        return self._points

    @points.setter
    def points(self, points):
        """Sets the points of this Assignment.


        :param points: The points of this Assignment.
        :type points: float
        """

        self._points = points

    @property
    def automatic_grading(self):
        """Gets the automatic_grading of this Assignment.


        :return: The automatic_grading of this Assignment.
        :rtype: str
        """
        return self._automatic_grading

    @automatic_grading.setter
    def automatic_grading(self, automatic_grading):
        """Sets the automatic_grading of this Assignment.


        :param automatic_grading: The automatic_grading of this Assignment.
        :type automatic_grading: str
        """
        allowed_values = ["unassisted", "auto", "full_auto"]  # noqa: E501
        if automatic_grading not in allowed_values:
            raise ValueError(
                "Invalid value for `automatic_grading` ({0}), must be one of {1}"
                .format(automatic_grading, allowed_values)
            )

        self._automatic_grading = automatic_grading

    @property
    def max_submissions(self):
        """Gets the max_submissions of this Assignment.


        :return: The max_submissions of this Assignment.
        :rtype: int
        """
        return self._max_submissions

    @max_submissions.setter
    def max_submissions(self, max_submissions):
        """Sets the max_submissions of this Assignment.


        :param max_submissions: The max_submissions of this Assignment.
        :type max_submissions: int
        """

        self._max_submissions = max_submissions

    @property
    def allow_files(self):
        """Gets the allow_files of this Assignment.


        :return: The allow_files of this Assignment.
        :rtype: bool
        """
        return self._allow_files

    @allow_files.setter
    def allow_files(self, allow_files):
        """Sets the allow_files of this Assignment.


        :param allow_files: The allow_files of this Assignment.
        :type allow_files: bool
        """

        self._allow_files = allow_files
