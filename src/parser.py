import os
import sys
from tqdm import tqdm
import pandas as pd
from datetime import datetime

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

from session_handler import SessionHandler
from agent_handler import AgentHandler

import argparse

parser = argparse.ArgumentParser(description="Parse chat histories for tohoku PJ")
parser.add_argument("--origin", dest="origin", help="Origin of softreef", type=str)
parser.add_argument("--user_id", dest="user_id", help="User id", type=str)
parser.add_argument("--password", dest="password", help="Password", type=str)
parser.add_argument("--project_id", dest="project_id", help="Project Id", type=str)
args = parser.parse_args()


class Parser:
    def __init__(
        self,
        origin: str = "http://localhost:8000",
        id: str = "admin",
        password: str = "password",
        project_id: str = "631a6a99-0b30-425a-bdf2-af4532ff9451",
    ) -> None:
        self.origin = self._get_candidate(
            candidates=[args.origin, os.environ.get("TOHOKU_ORIGIN"), origin]
        )
        self.id = self._get_candidate(
            candidates=[args.user_id, os.environ.get("TOHOKU_USER_ID"), id]
        )
        self.password = self._get_candidate(
            candidates=[args.password, os.environ.get("TOHOKU_PASSWORD"), password]
        )
        self.project_id = self._get_candidate(
            candidates=[
                args.project_id,
                os.environ.get("TOHOKU_PROJECT_ID"),
                project_id,
            ]
        )
        self.authorization = (self.id, self.password)

        self.session_handler = SessionHandler(
            origin=self.origin,
            id=self.id,
            password=self.password,
            project_id=self.project_id,
        )
        self.agent_handler = AgentHandler(
            origin=self.origin,
            id=self.id,
            password=self.password,
            project_id=self.project_id,
        )

    def _get_candidate(self, candidates: list) -> str:
        for candidate in candidates:
            if not candidate is None:
                return candidate
        logger.error("No given candidate has valid value.")
        raise Exception

    def parse_general_messages(self, messages: list) -> pd.DataFrame:
        """
        Is is assumed that "messages" are archived in such a way that the following conditions are met.
        - A user message and a response from the LLM.
        - The above two messages are in the save format in all conversation rallied as one lump.
        """
        general_message_rows = pd.DataFrame()
        for i_start in range(0, len(messages), 2):
            new_row = pd.DataFrame(
                {
                    "session_message_timestamp": messages[i_start].get("timestamp"),
                    "session_message_system_content_text": None,  # For consistency
                    "session_message_user_content_text": messages[i_start]
                    .get("content")[0]
                    .get("text"),  # Message with "role" = "user"
                    "session_message_rag_content_text": None,  # For consistency
                    "session_message_assistant_content_text": messages[i_start + 1]
                    .get("content")[0]
                    .get("text"),  # Message with "role" = "assistant"
                },
                index=[len(general_message_rows)],
            )

            general_message_rows = pd.concat(
                [general_message_rows, new_row], ignore_index=True
            )

        return general_message_rows

    def parse_prompt_messages(self, messages: list) -> pd.DataFrame:
        """
        It is assumed that "messages" are archived in such a way that the following conditions are met.
        - The first is a message that is applied to the entire session specified by the user.
        - Then a user input and a response from the LLM.
        - The above two messages are in the same format in all conversation rallied as one lump.
        """
        prompt_message_rows = pd.DataFrame()
        for i_start in range(1, len(messages), 2):
            new_row = pd.DataFrame(
                {
                    "session_message_timestamp": messages[i_start].get("timestamp"),
                    "session_message_system_content_text": messages[0]
                    .get("content")[0]
                    .get("text"),  # Message with "role" = "system"
                    "session_message_user_content_text": messages[i_start]
                    .get("content")[0]
                    .get("text"),  # Message with "role" = "user"
                    "session_message_rag_content_text": None,  # For consistency
                    "session_message_assistant_content_text": messages[i_start + 1]
                    .get("content")[0]
                    .get("text"),  # Message with "role" = "assistant"
                },
                index=[len(prompt_message_rows)],
            )

            prompt_message_rows = pd.concat(
                [prompt_message_rows, new_row], ignore_index=True
            )

        return prompt_message_rows

    def parse_rag_messages(self, messages: list) -> pd.DataFrame:
        """
        it is assumed that "messages" are archived in such a way that the following conditions are met.
        - The first is a message that is applied to the entire session specified by the user.
        - Then a user input, an associated RAG texts and a response from the LLM.
        - The above three messages are in the same format in all conversation rallied as one lump.
        """
        rag_messages_rows = pd.DataFrame()
        for i_start in range(1, len(messages), 3):
            new_row = pd.DataFrame(
                {
                    "session_message_timestamp": messages[i_start].get("timestamp"),
                    "session_message_system_content_text": messages[0]
                    .get("content")[0]
                    .get("text"),  # Message with "role" = "system"
                    "session_message_user_content_text": messages[i_start]
                    .get("content")[0]
                    .get("text"),  # Message with "role" = "user"
                    "session_message_rag_content_text": messages[i_start + 1]
                    .get("content")[0]
                    .get("text"),  # Message with "role" = "system"
                    "session_message_assistant_content_text": messages[i_start + 2]
                    .get("content")[0]
                    .get("text"),  # Message with "role" = "assistant"
                },
                index=[len(rag_messages_rows)],
            )

            rag_messages_rows = pd.concat(
                [rag_messages_rows, new_row], ignore_index=True
            )

        return rag_messages_rows

    def parse(
        self,
        start_datetime: str = "2024-11-24T00:00:00.000000+09:00",
        output_file_name: str = f"{os.path.dirname(__file__)}/../histories/histories.csv",
        sheet_name: str | None = None,
    ) -> None:
        data_frame = pd.DataFrame()

        # Retrieve all sessions associated with the project
        sessions = self.session_handler.get_sessions_created_after_given_datetime(
            datetime=start_datetime
        )

        for session in tqdm(sessions, desc="Sessions"):
            # Retrieve agent id from each session
            agent_id = session.get("agent")
            agent = self.agent_handler.get_agent(agent_id=agent_id)
            agent_name = agent.get("name")
            agent_type = agent.get("type")
            agent_context_category = agent.get("context").get("category")
            agent_context_description = agent.get("context").get("description")
            agent_context_source_text = agent.get("context").get("source_text")

            # Retrieve information associated with the current session
            session_name = session.get("name")
            session_created_user_name = session.get("created_user_name")

            # Retrieve messages associated with the current session
            messages = session.get("messages")
            if agent_context_category == "prompt":
                messages_rows = self.parse_prompt_messages(messages=messages)
            elif agent_context_category == "general":
                messages_rows = self.parse_general_messages(messages=messages)
            elif agent_context_category == "rag":
                messages_rows = self.parse_rag_messages(messages=messages)
            else:
                logger.error(
                    f'Even one of the ["prompt", "general", "rag"] is available as a message category, "{agent_context_category}" was detected.\nPlease configure your agent properly. Following categories are supported.'
                )
                continue

            for _, row in messages_rows.iterrows():
                new_row = pd.DataFrame(
                    {
                        **{
                            "agent_name": agent_name,
                            "agent_type": agent_type,
                            "agent_context_category": agent_context_category,
                            "agent_context_description": agent_context_description,
                            "agent_context_source_text": agent_context_source_text,
                            "session_name": session_name,
                            "session_created_user_name": session_created_user_name,
                        },
                        **{key: value for key, value in row.items()},
                    },
                    index=[len(data_frame)],
                )
                data_frame = pd.concat([data_frame, new_row], ignore_index=True)

        if not os.path.exists(os.path.dirname(output_file_name)):
            os.makedirs(os.path.dirname(output_file_name), exist_ok=False)

        format = output_file_name.split(".")[-1]
        if format == "xlsx":
            sheet_name = (
                datetime.now().strftime("%Y-%m-%d")
                if sheet_name is None
                else sheet_name
            )
            with pd.ExcelWriter(output_file_name, engine="openpyxl") as writer:
                data_frame.to_excel(writer, sheet_name=sheet_name)
        if format == "csv":
            data_frame.to_csv(output_file_name, index=False)

        logger.info(f"{output_file_name} was generated.")


if __name__ == "__main__":
    parser = Parser()
    parser.parse(
        output_file_name=f"{os.path.dirname(__file__)}/../histories/sessions.xlsx"
    )
