import os
import re
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
        origin: str = "http://localhost:8000",
        id="admin",
        password="password",
        project_id="631a6a99-0b30-425a-bdf2-af4532ff9451",
    ):
        self.origin = origin
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
            f"{self.origin}/api/genai/v1/projects/{self.project_id}/sessions/{session_id}",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)

    def get_sessions(self):
        response = requests.get(
            f"{self.origin}/api/genai/v1/projects/{self.project_id}/sessions",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)

    def get_sorted_sessions(self, sorted_by: str = "created_at"):
        sessions = self.get_sessions()
        sorted_sessions = sorted(sessions, key=lambda x: x[sorted_by])
        return sorted_sessions

    def get_filtered_sessions(
        self,
        excluded_user_name_regexes: list = [],
        start_datetime: str = "2000-12-31T00:00:00.000000+09:00",
        end_datetime: str = "2100-12-31T00:00:00.000000+09:00",
    ):
        sessions = self.get_sessions()
        sessions = self.get_filtered_sessions_by_user_name(
            sessions=sessions, excluded_user_name_regexes=excluded_user_name_regexes
        )
        sessions = self.get_filtered_sessions_by_datetime(
            sessions=sessions, start_datetime=start_datetime, end_datetime=end_datetime
        )

        return sessions

    def get_filtered_sessions_by_user_name(
        self, sessions: list, excluded_user_name_regexes: list = []
    ):
        filtered_sessions = []
        for session in sessions:
            exclude = False
            create_user_name = session.get("created_user_name")
            for regex in excluded_user_name_regexes:
                if re.match(regex, create_user_name):
                    exclude = True
                    break
            if not exclude:
                filtered_sessions.append(session)

        return filtered_sessions

    def get_filtered_sessions_by_datetime(
        self,
        sessions: list,
        start_datetime: str = "2000-12-31T00:00:00.000000+09:00",
        end_datetime: str = "2100-12-31T00:00:00.000000+09:00",
    ):
        return [
            session
            for session in sessions
            if parser.parse(start_datetime) < parser.parse(session.get("created_at"))
            and parser.parse(session.get("created_at")) < parser.parse(end_datetime)
        ]

    def get_messages(self, session_id: str):
        response = requests.get(
            f"{self.origin}/api/genai/v1/projects/{self.project_id}/sessions/{session_id}/messages",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)

    def create_session(self):
        response = requests.post(
            f"{self.origin}/api/genai/v1/projects/{self.project_id}/sessions",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)

    def delete_session(self, session_id: str):
        response = requests.delete(
            f"{self.origin}/api/genai/v1/projects/{self.project_id}/sessions/{session_id}",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)


if __name__ == "__main__":
    handler = SessionHandler()
    pprint.pprint(handler.get_sorted_sessions())
