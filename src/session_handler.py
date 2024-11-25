import os
import pprint
import requests
from dateutil import parser

# Logging
import logging

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
handler_format = logging.Formatter(
    "%(asctime)s : [%(name)s - %(lineno)d] %(levelname)-8s - %(message)s"
)
stream_handler.setFormatter(handler_format)
logger.addHandler(stream_handler)


class SessionHandler:
    def __init__(
        self,
        host_url: str = "http://localhost:8000",
        id="admin",
        password="password",
        project_id="631a6a99-0b30-425a-bdf2-af4532ff9451",
    ):
        self.host_url = host_url
        self.id = id
        self.password = password
        self.project_id = project_id
        self.authorization = (self.id, self.password)

    def return_json_or_raise_exception(self, response):
        try:
            return response.json()
        except Exception as e:
            logger.critical(f"An error occurred: {e}")
            raise

    def get_session(self, session_id: str):
        response = requests.get(
            f"{self.host_url}/api/genai/v1/projects/{self.project_id}/sessions/{session_id}",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)

    def get_sessions(self):
        response = requests.get(
            f"{self.host_url}/api/genai/v1/projects/{self.project_id}/sessions",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)

    def get_sorted_sessions(self, sorted_by: str = "created_at"):
        sessions = self.get_sessions()
        sorted_sessions = sorted(sessions, key=lambda x: x[sorted_by])
        return sorted_sessions

    def get_sessions_created_after_given_datetime(self, datetime: str):
        return [
            session
            for session in self.get_sessions()
            if parser.parse(datetime) < parser.parse(session.get("created_at"))
        ]

    def get_messages(self, session_id: str):
        response = requests.get(
            f"{self.host_url}/api/genai/v1/projects/{self.project_id}/sessions/{session_id}/messages",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)

    def create_session(self):
        response = requests.post(
            f"{self.host_url}/api/genai/v1/projects/{self.project_id}/sessions",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)

    def delete_session(self, session_id: str):
        response = requests.delete(
            f"{self.host_url}/api/genai/v1/projects/{self.project_id}/sessions/{session_id}",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)


if __name__ == "__main__":
    handler = SessionHandler()
    pprint.pprint(handler.get_sorted_sessions())
