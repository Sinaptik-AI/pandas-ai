import threading
from importlib import reload

_engine = "pandas"
_lock: threading.RLock = threading.RLock()


def set_pd_engine(engine: str = "pandas"):
    global _engine
    if engine.lower() not in ("modin", "pandas"):
        raise ValueError(
            f"Unknown engine {engine}. Valid options are ('modin', 'pandas')"
        )

    if engine != _engine:
        with _lock:
            _engine = engine
            _reload_pd()


def _reload_pd():
    import pandasai

    reload(pandasai.pandas)
