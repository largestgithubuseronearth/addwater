import os, os.path, tarfile, logging, json, requests
from .paths import DOWNLOAD_DIR
from typing import Optional

log = logging.getLogger(__name__)

# TODO how to make download asynchronous? Is that even worthwhile?
# TODO delete old versions and make them all the same name
def download_release(tarball_url: str, version: int, appname: str) -> None:
    appname = appname.lower()
    log.info(f"Update available ({appname} v{version}). Downloading now...")

    try:
        response = requests.get(tarball_url) # TODO use stream flag
    except requests.RequestException as e:
        log.error(f"Github download failed [{e}]")
        raise err.NetworkException('Download failed.')

    p = os.path.join(DOWNLOAD_DIR, f"{app}.tar.gz")
    with open(file=p, mode="wb", encoding='utf-8') as file:
        file.write(response.content)

    log.info("Github download SUCCESS!")

    try:
        extract_theme_release(appname=appname, version=version)
    except (FileNotFoundError, tarfile.TarError) as e:
        log.critical(e)
        raise err.NetworkException('Theme files failed to extract')


def extract_theme_release(appname: str, version: int) -> None:
    appname = appname.lower()
    zipfile = os.path.join(DOWNLOAD_DIR, f"{appname}.tar.gz")
    extract_dir = os.path.join(DOWNLOAD_DIR, f"{appname}-extracted/")

    if os.path.exists(extract_dir):
        log.info(f"{appname} already extracted. Skipping.")
        return os.path.join(extract_dir, f"{appname}-gnome-theme")
    if not os.path.exists(zipfile):
        log.error(f"Release zip doesn't exist: {zipfile}")
        raise FileNotFoundError

    with tarfile.open(zipfile) as tar:
        tar.extractall(path=extract_dir, filter="data")

    with os.scandir(path=extract_dir) as scan:
        for each in scan:
            if each.name.startswith(f"rafaelmardojai-{appname}-gnome-theme"):
                old = os.path.join(extract_dir, each.name)
                new = os.path.join(extract_dir, f"{appname}-gnome-theme")
                os.rename(old, new)
    os.remove(zipfile)
    log.info(f"{appname} tarball extracted successfully.")

