import os
import sys
import pprint
import requests
import json

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


class AgentHandler:
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

    def get_agent(self, agent_id: str):
        response = requests.get(
            f"{self.origin}/api/genai/v1/projects/{self.project_id}/agents/{agent_id}",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)

    def get_agents(self):
        response = requests.get(
            f"{self.origin}/api/genai/v1/projects/{self.project_id}/agents",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)

    def create_agent(self, name: str, type: str, context: dict):
        data = {"name": name, "type": type, "context": context}
        response = requests.post(
            f"{self.origin}/api/genai/v1/projects/{self.project_id}/agents",
            auth=self.authorization,
            data=json.dump(data),
        )
        return self.return_json_or_raise_exception(response=response)

    def delete_agent(self, agent_id: str):
        response = requests.delete(
            f"{self.origin}/api/genai/v1/projects/{self.project_id}/agents/{agent_id}",
            auth=self.authorization,
        )
        return self.return_json_or_raise_exception(response=response)


if __name__ == "__main__":
    handler = AgentHandler()
    pprint.pprint(handler.get_agents())
