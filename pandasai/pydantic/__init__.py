try:
    from pydantic.v1 import *  # noqa: F403 # type: ignore
except ImportError:
    from pydantic import *  # noqa: F403 # type: ignore
