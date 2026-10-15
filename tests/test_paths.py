import os
import pytest
import shutil
import sys

from os.path import exists
from pathlib import Path

from . import suite
sys.path.insert(1, suite.pkgdatadir)

from addwater.model.paths import *

TEST_ROOT = Path("/tmp/addwater/test")
TEST_HOME = TEST_ROOT / "home"

@pytest.fixture
def fake_env(monkeypatch) -> None:
    TEST_HOME.mkdir(exist_ok=False, parents=True)

    monkeypatch.setenv("HOME", str(TEST_HOME))
    monkeypatch.delenv("container")

    monkeypatch.setenv("XDG_CACHE_HOME",  str(TEST_HOME / ".thecachedir"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(TEST_HOME / ".theconfigurationdir"))
    monkeypatch.setenv("XDG_DATA_HOME",   str(TEST_HOME / ".thedatadir"))

    yield None

    shutil.rmtree(TEST_ROOT)

@pytest.fixture
def fake_env_flatpak(monkeypatch) -> None:
    TEST_HOME.mkdir(exist_ok=False, parents=True)

    SANDBOX_HOME = TEST_HOME / ".var/app/dev.qwery.AddWater"

    monkeypatch.setenv("HOME", str(TEST_HOME))
    monkeypatch.setenv("container", "flatpak")

    monkeypatch.setenv("XDG_CACHE_HOME",  str(SANDBOX_HOME / ".thecachedir"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(SANDBOX_HOME / ".theconfigurationdir"))
    monkeypatch.setenv("XDG_DATA_HOME",   str(SANDBOX_HOME / "thedatadir"))

    monkeypatch.setenv("HOST_XDG_CACHE_HOME",  str(TEST_HOME / ".thecachedir"))
    monkeypatch.setenv("HOST_XDG_CONFIG_HOME", str(TEST_HOME / ".theconfigurationdir"))
    monkeypatch.setenv("HOST_XDG_DATA_HOME",   str(TEST_HOME / ".thedatadir"))

    yield None

    shutil.rmtree(TEST_ROOT)

@pytest.fixture
def fake_env_empty(monkeypatch) -> None:
    TEST_HOME.mkdir(exist_ok=False, parents=True)

    monkeypatch.setenv("HOME", str(TEST_HOME))
    monkeypatch.delenv("container", raising=False)

    monkeypatch.delenv("XDG_CACHE_HOME",  raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME",   raising=False)

    monkeypatch.delenv("HOST_XDG_CACHE_HOME",  raising=False)
    monkeypatch.delenv("HOST_XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("HOST_XDG_DATA_HOME",   raising=False)

    yield None 

    shutil.rmtree(TEST_ROOT)

def test_paths(fake_env) -> None:
    USER_CACHE = Path(environ["XDG_CACHE_HOME"])
    USER_CONFIG = Path(environ["XDG_CONFIG_HOME"])
    USER_DATA  = Path(environ["XDG_DATA_HOME"])

    assert not in_flatpak()
    assert flatpak_data_home() is None
    assert user_config()    == USER_CONFIG
    assert user_data_home() == USER_DATA
    assert aw_cache_dir()   == USER_CACHE / "addwater"
    assert aw_config_dir()  == USER_CONFIG / "addwater"
    assert aw_data_dir()    == USER_DATA / "addwater"

def test_paths_in_flatpak(fake_env_flatpak) -> None:
    USER_CONFIG    = Path(environ["HOST_XDG_CONFIG_HOME"])
    USER_DATA      = Path(environ["HOST_XDG_DATA_HOME"])
    FLATPAK_CACHE  = Path(environ["XDG_CACHE_HOME"])
    FLATPAK_CONFIG = Path(environ["XDG_CONFIG_HOME"])
    FLATPAK_DATA   = Path(environ["XDG_DATA_HOME"])

    assert in_flatpak()
    assert flatpak_data_home() == FLATPAK_DATA
    assert user_data_home()    == USER_DATA
    assert user_config()       == USER_CONFIG
    assert aw_cache_dir()      == FLATPAK_CACHE / "addwater"
    assert aw_config_dir()     == FLATPAK_CONFIG / "addwater"
    assert aw_data_dir()       == FLATPAK_DATA / "addwater"

def test_paths_xdg_default(fake_env_empty) -> None:
    HOME        = Path(environ["HOME"])
    USER_CACHE  = HOME / ".cache"
    USER_CONFIG = HOME / ".config"
    USER_DATA   = HOME / ".local/share"

    assert not in_flatpak()
    assert flatpak_data_home() is None
    assert user_data_home() == USER_DATA
    assert user_config()    == USER_CONFIG
    assert aw_cache_dir()   == USER_CACHE / "addwater"
    assert aw_data_dir()    == USER_DATA / "addwater"

