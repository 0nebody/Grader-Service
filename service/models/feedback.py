# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from models.base_model_ import Model
from service import util


class Feedback(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, submission_id=None):  # noqa: E501
        """Feedback - a model defined in OpenAPI

        :param id: The id of this Feedback.  # noqa: E501
        :type id: int
        :param submission_id: The submission_id of this Feedback.  # noqa: E501
        :type submission_id: int
        """
        self.openapi_types = {
            'id': int,
            'submission_id': int
        }

        self.attribute_map = {
            'id': 'id',
            'submission_id': 'submission_id'
        }

        self._id = id
        self._submission_id = submission_id

    @classmethod
    def from_dict(cls, dikt) -> 'Feedback':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Feedback of this Feedback.  # noqa: E501
        :rtype: Feedback
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this Feedback.


        :return: The id of this Feedback.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Feedback.


        :param id: The id of this Feedback.
        :type id: int
        """

        self._id = id

    @property
    def submission_id(self):
        """Gets the submission_id of this Feedback.


        :return: The submission_id of this Feedback.
        :rtype: int
        """
        return self._submission_id

    @submission_id.setter
    def submission_id(self, submission_id):
        """Sets the submission_id of this Feedback.


        :param submission_id: The submission_id of this Feedback.
        :type submission_id: int
        """

        self._submission_id = submission_id