from os import PathLike, environ
from pathlib import Path

# Flatpak overrides XDG_DATA_HOME so we need to also check HOST_XDG_DATA_HOME
_user_data_home:     Path        = None  # Real host data dir
_flatpak_data_home:  Path | None = None  # Container data dir if exists
_user_config:        Path        = None

# These should always prefer container path if in one
_aw_data_dir:    Path = None
_aw_config_dir:  Path = None
_aw_cache_dir:   Path = None

def user_home() -> Path:
    """User's HOME dir"""
    if not (path := environ.get("HOME")):
        raise OSError("env HOME is not set. bail out!")

    return ensure_exists(path)

def user_data_home() -> Path:
    """User's true XDG_DATA_HOME dir. To use the Flatpak sandboxed dir, use
    `flatpak_data_home()` instead"""
    key = "XDG_DATA_HOME"
    if in_flatpak():
        key = "HOST_" + key

    if not (path := environ.get(key)):
        path = "~/.local/share"

    return ensure_exists(path)

def user_config() -> Path:
    """User's true XDG_CONFIG_HOME dir"""
    key = "XDG_CONFIG_HOME"
    if in_flatpak():
        key = "HOST_" + key

    if not (path := environ.get(key)):
        path = "~/.config"

    return ensure_exists(path)

def aw_data_dir() -> Path:
    """Add Water data dir. Always prefer sandbox dir if in one"""
    if in_flatpak():
        path = flatpak_data_home() / 'addwater'
    else:
        path = user_data_home() / 'addwater'

    return ensure_exists(path)

def aw_config_dir() -> Path:
    """Add Water config dir. Always prefer sandbox dir if in one"""
    if not (path := environ.get("XDG_CONFIG_HOME")):
        path = "~/.config"

    return ensure_exists(Path(path) / 'addwater')

def aw_cache_dir() -> Path:
    """Add Water cache dir. Always prefer sandbox dir if in one"""
    if not (path := environ.get("XDG_CACHE_HOME")):
        path = "~/.cache"

    return ensure_exists(Path(path) / 'addwater')

def ensure_exists(path: Path | PathLike) -> Path:
    """Ensure a Path already exists in the filesystem"""
    new = Path(path).expanduser()
    new.mkdir(exist_ok=True, parents=True)
    return new

def flatpak_data_home() -> Path | None:
    """Returns the sandboxed XDG_DATA_HOME dir. If not inside Flatpak,
    returns None"""
    if not in_flatpak():
        return None

    return ensure_exists(environ.get("XDG_DATA_HOME"))

def in_flatpak() -> bool:
    """Check for signs that we're inside a Flatpak sandbox"""
    return environ.get("container") == "flatpak"

