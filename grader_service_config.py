import os

c.GraderService.service_host = "127.0.0.1"
c.GraderService.grader_service_dir = os.path.expanduser("~/grader_service_dir")

c.GraderServer.hub_service_name = "grader"
c.GraderServer.hub_api_token = "7572f93a2e7640999427d9289c8318c0"
c.GraderServer.hub_api_url = "http://127.0.0.1:8081/hub/api"
c.GraderServer.hub_base_url = "/"

c.DataBaseManager.db_dialect = "sqlite"
c.DataBaseManager.db_host = "/" + os.path.abspath(os.path.dirname(__file__) + "/service/grader.db")