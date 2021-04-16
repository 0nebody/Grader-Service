# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from common.models.base_model_ import Model
from common.models.grading_result import GradingResult
from common.models.submission import Submission
from common import util

from common.models.grading_result import GradingResult  # noqa: E501
from common.models.submission import Submission  # noqa: E501

class InlineResponse200Submissions(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, submission=None, grading_result=None):  # noqa: E501
        """InlineResponse200Submissions - a model defined in OpenAPI

        :param submission: The submission of this InlineResponse200Submissions.  # noqa: E501
        :type submission: Submission
        :param grading_result: The grading_result of this InlineResponse200Submissions.  # noqa: E501
        :type grading_result: GradingResult
        """
        self.openapi_types = {
            'submission': Submission,
            'grading_result': GradingResult
        }

        self.attribute_map = {
            'submission': 'submission',
            'grading_result': 'grading_result'
        }

        self._submission = submission
        self._grading_result = grading_result

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponse200Submissions':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_200_submissions of this InlineResponse200Submissions.  # noqa: E501
        :rtype: InlineResponse200Submissions
        """
        return util.deserialize_model(dikt, cls)

    @property
    def submission(self):
        """Gets the submission of this InlineResponse200Submissions.


        :return: The submission of this InlineResponse200Submissions.
        :rtype: Submission
        """
        return self._submission

    @submission.setter
    def submission(self, submission):
        """Sets the submission of this InlineResponse200Submissions.


        :param submission: The submission of this InlineResponse200Submissions.
        :type submission: Submission
        """

        self._submission = submission

    @property
    def grading_result(self):
        """Gets the grading_result of this InlineResponse200Submissions.


        :return: The grading_result of this InlineResponse200Submissions.
        :rtype: GradingResult
        """
        return self._grading_result

    @grading_result.setter
    def grading_result(self, grading_result):
        """Sets the grading_result of this InlineResponse200Submissions.


        :param grading_result: The grading_result of this InlineResponse200Submissions.
        :type grading_result: GradingResult
        """

        self._grading_result = grading_result
