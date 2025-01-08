"""Unit tests for the import_optional_dependency function.

Source: Taken from pandas/tests/test_optional_dependency.py
"""

import sys
import types

import pytest

from pandasai.core.code_execution.environment import (
    VERSIONS,
    get_environment,
    import_dependency,
)
from pandasai.core.code_execution.safe_libs.restricted_matplotlib import (
    RestrictedMatplotlib,
)
from pandasai.core.code_execution.safe_libs.restricted_numpy import RestrictedNumpy
from pandasai.core.code_execution.safe_libs.restricted_pandas import RestrictedPandas


def test_import_optional():
    match = "Missing .*notapackage.* pip .* conda .* notapackage"
    with pytest.raises(ImportError, match=match) as exc_info:
        import_dependency("notapackage")
    # The original exception should be there as context:
    assert isinstance(exc_info.value.__context__, ImportError)

    result = import_dependency("notapackage", errors="ignore")
    assert result is None


def test_xlrd_version_fallback():
    pytest.importorskip("xlrd")
    import_dependency("xlrd")


def test_bad_version(monkeypatch):
    name = "fakemodule"
    module = types.ModuleType(name)
    module.__version__ = "0.9.0"
    sys.modules[name] = module
    monkeypatch.setitem(VERSIONS, name, "1.0.0")

    match = "Pandas requires .*1.0.0.* of .fakemodule.*'0.9.0'"
    with pytest.raises(ImportError, match=match):
        import_dependency("fakemodule")

    # Test min_version parameter
    result = import_dependency("fakemodule", min_version="0.8")
    assert result is module

    with pytest.warns(UserWarning):
        result = import_dependency("fakemodule", errors="warn")
    assert result is None

    module.__version__ = "1.0.0"  # exact match is OK
    result = import_dependency("fakemodule")
    assert result is module


def test_submodule(monkeypatch):
    # Create a fake module with a submodule
    name = "fakemodule"
    module = types.ModuleType(name)
    module.__version__ = "0.9.0"
    sys.modules[name] = module
    sub_name = "submodule"
    submodule = types.ModuleType(sub_name)
    setattr(module, sub_name, submodule)
    sys.modules[f"{name}.{sub_name}"] = submodule
    monkeypatch.setitem(VERSIONS, name, "1.0.0")

    match = "Pandas requires .*1.0.0.* of .fakemodule.*'0.9.0'"
    with pytest.raises(ImportError, match=match):
        import_dependency("fakemodule.submodule")

    with pytest.warns(UserWarning):
        result = import_dependency("fakemodule.submodule", errors="warn")
    assert result is None

    module.__version__ = "1.0.0"  # exact match is OK
    result = import_dependency("fakemodule.submodule")
    assert result is submodule


def test_no_version_raises(monkeypatch):
    name = "fakemodule"
    module = types.ModuleType(name)
    sys.modules[name] = module
    monkeypatch.setitem(VERSIONS, name, "1.0.0")

    with pytest.raises(ImportError, match="Can't determine .* fakemodule"):
        import_dependency(name)


def test_env_for_necessary_deps():
    env = get_environment([])
    assert "pd" in env
    assert "plt" in env
    assert "np" in env


def test_env_for_security():
    env = get_environment([], secure=True)
    assert "pd" in env and isinstance(env["pd"], RestrictedPandas)
    assert "plt" in env and isinstance(env["plt"], RestrictedMatplotlib)
    assert "np" in env and isinstance(env["np"], RestrictedNumpy)

    env = get_environment([], secure=False)
    assert "pd" in env and not isinstance(env["pd"], RestrictedPandas)
    assert "plt" in env and not isinstance(env["plt"], RestrictedMatplotlib)
    assert "np" in env and not isinstance(env["np"], RestrictedNumpy)
