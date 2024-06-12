import os
from typing import List

import pandas as pd
from fastapi import Depends, FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import router
from app.controllers.workspace import WorkspaceController
from app.controllers.user import UserController
from app.models import Dataset, Workspace, User
from app.repositories.dataset import DatasetRepository
from app.repositories.workspace import WorkspaceRepository
from app.repositories.user import UserRepository
from core.config import config
from core.database.session import session
from core.exceptions import CustomException
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (
    AuthBackend,
    AuthenticationMiddleware,
    SQLAlchemyMiddleware,
)
from core.utils.dataframe import convert_dataframe_to_dict


def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )


def init_routers(app_: FastAPI) -> None:
    app_.include_router(router)


def init_listeners(app_: FastAPI) -> None:
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            AuthenticationMiddleware,
            backend=AuthBackend(),
            on_error=on_auth_error,
        ),
        Middleware(SQLAlchemyMiddleware),
        # Middleware(ResponseLoggerMiddleware),
    ]
    return middleware


async def init_user():
    user_repository = UserRepository(User, db_session=session)
    space_repository = WorkspaceRepository(Workspace, db_session=session)
    controller = UserController(user_repository, space_repository)
    await controller.create_default_user()
    users = await controller.get_all(limit=1, join_={"memberships"})
    return users[0]


def read_csv_files_from_directory(directory_path):
    """
    Reads all CSV files from the specified directory and loads them into pandas DataFrames.

    :param directory_path: The path to the directory containing CSV files.
    :return: A dictionary where keys are filenames and values are pandas DataFrames.
    """
    dataframes = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path)

                dataframes.append(
                    {
                        "head": convert_dataframe_to_dict(df.head()),
                        "file_name": file,
                        "file_path": file_path,
                    }
                )

    return dataframes


async def init_database():
    user = await init_user()
    directory_path = os.path.join(os.path.dirname(__file__), "..", "data")
    datasets = read_csv_files_from_directory(directory_path)
    space_repository = WorkspaceRepository(Workspace, db_session=session)

    space = await space_repository.create_default_space_in_org(
        organization_id=user.memberships[0].organization_id, user_id=user.id
    )
    dataset_repository = DatasetRepository(Dataset, db_session=session)
    space_controller = WorkspaceController(
        space_repository=space_repository, dataset_repository=dataset_repository
    )

    await space_controller.reset_space_datasets(space.id)
    await space_controller.add_csv_datasets(datasets, user, space.id)


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="PandasAI Server",
        description="PandasAI Backend server",
        version="1.0.0",
        docs_url=None if config.ENVIRONMENT == "production" else "/docs",
        redoc_url=None if config.ENVIRONMENT == "production" else "/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    init_listeners(app_=app_)

    @app_.on_event("startup")
    async def on_startup():
        await init_database()

    return app_


app = create_app()
