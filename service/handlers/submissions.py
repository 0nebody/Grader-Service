from registry import register_handler
from handlers.base_handler import GraderBaseHandler, authorize
from orm.assignment import Assignment
from orm.base import DeleteState
from orm.submission import Submission
from orm.takepart import Role, Scope
from sqlalchemy.sql.expression import func
from tornado.httpclient import HTTPError


@register_handler(
    path=r"\/lectures\/(?P<lecture_id>\d*)\/assignments\/(?P<assignment_id>\d*)\/submissions\/?"
)
class SubmissionHandler(GraderBaseHandler):
    @authorize([Scope.student, Scope.tutor, Scope.instructor])
    async def get(self, lecture_id: int, assignment_id: int):
        latest = self.get_argument("latest", None) == "true"
        instructor_version = (
            self.get_argument("instructor-version", None) == "true"
        )

        role = self.session.query(Role).get((self.user.name, lecture_id))
        if instructor_version and role.role < Scope.tutor:
            self.error_message = "Unauthorized"
            raise HTTPError(403)

        if instructor_version:
            assignment = self.session.query(Assignment).get(assignment_id)
            if assignment is None or assignment.deleted == DeleteState.deleted:
                self.error_message = "Not Found"
                raise HTTPError(404)
            submissions = []
            if latest:
                submissions = (
                    self.session.query(Submission.id,Submission.status,Submission.score, Submission.username,Submission.assignid,func.max(Submission.date))
                    .filter(Submission.assignid == assignment_id)
                    .group_by(Submission.username).all()
                )
            else:
                submissions = assignment.submissions
            user_map = {}
            sub: Submission
            for sub in submissions:
                if sub.username in user_map:
                    user_map[sub.username]["submissions"].append(sub)
                else:
                    user_map[sub.username] = {"user": sub.user, "submissions": [sub]}
            response = list(user_map.values())
        else:
            if latest:
                submissions = (
                    self.session.query(Submission.id,Submission.status,Submission.score, Submission.username,Submission.assignid,func.max(Submission.date))
                    .filter(Submission.assignid == assignment_id, Submission.username == role.username)
                    .group_by(Submission.username)
                )
            else:
                submissions = role.user.submissions
            response = [
                {
                    "user": role.user,
                    "submissions": [
                        s for s in submissions if s.assignid == int(assignment_id)
                    ],
                }
            ]
        self.write_json(response)

    @authorize([Scope.student, Scope.tutor, Scope.instructor])
    async def post(self, lecture_id: int, assignment_id: int):
        pass


@register_handler(
    path=r"\/lectures\/(?P<lecture_id>\d*)\/assignments\/(?P<assignment_id>\d*)\/feedback\/?"
)
class FeedbackHandler(GraderBaseHandler):
    @authorize([Scope.student, Scope.tutor, Scope.instructor])
    async def get(self, lecture_id: int, assignment_id: int):
        latest = self.get_argument("latest", False)
        instructor_version = self.get_argument("instructor-version", False)
        pass


@register_handler(
    path=r"\/lectures\/(?P<lecture_id>\d*)\/assignments\/(?P<assignment_id>\d*)\/feedback\/(?P<feedback_id>\d*)\/?"
)
class FeedbackObjectHandler(GraderBaseHandler):
    @authorize([Scope.student, Scope.tutor, Scope.instructor])
    async def get(self, lecture_id: int, assignment_id: int, feedback_id: int):
        pass