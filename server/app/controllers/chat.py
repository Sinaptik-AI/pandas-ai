import os
import shutil
import uuid
from typing import List

import pandas as pd
from pandasai import Agent
from pandasai.connectors.pandas import PandasConnector
from pandasai.helpers.path import find_project_root

from app.models import Dataset, User
from app.repositories import UserRepository
from app.repositories.space import SpaceRepository
from app.schemas.requests.chat import ChatRequest
from core.constants import CHAT_FALLBACK_MESSAGE
from core.controller import BaseController
from core.utils.dataframe import load_df
from core.utils.response_parser import JsonResponseParser


class ChatController(BaseController[User]):
    def __init__(
        self, user_repository: UserRepository, space_repository: SpaceRepository
    ):
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository
        self.space_repository = space_repository

    async def chat(self, chat_request: ChatRequest) -> List[dict]:
        datasets: List[Dataset] = await self.space_repository.get_space_datasets(
            chat_request.space_id
        )

        connectors = []
        for dataset in datasets:
            config = dataset.connector.config
            df = pd.read_csv(config["file_path"])
            connector = PandasConnector(
                {"original_df": df},
                name=dataset.name,
                description=dataset.description,
                custom_head=(load_df(dataset.head) if dataset.head else None),
                field_descriptions=dataset.field_descriptions,
            )
            connectors.append(connector)

        path_plot_directory = find_project_root() + "/exports/" + str(uuid.uuid4())

        config = {
            "enable_cache": False,
            "response_parser": JsonResponseParser,
            "save_charts": True,
            "save_charts_path": path_plot_directory,
        }

        agent = Agent(connectors, config=config)

        response = agent.chat(chat_request.query)

        if os.path.exists(path_plot_directory):
            shutil.rmtree(path_plot_directory)

        if isinstance(response, str) and (
            response.startswith("Unfortunately, I was not able to")
        ):
            return [
                {
                    "type": "string",
                    "message": CHAT_FALLBACK_MESSAGE,
                    "value": CHAT_FALLBACK_MESSAGE,
                }
            ]

        return [response]
