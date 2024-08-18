import os, os.path, tarfile, logging
from .paths import DOWNLOAD_DIR
from typing import Optional

log = logging.getLogger(__name__)

def extract_theme_release(appname, version) -> Optional[str]:
    appname = appname.lower()

    # TODO refactor to be cleaner
    filename = f"{appname}-{version}"
    zipfile = os.path.join(DOWNLOAD_DIR, f"{filename}.tar.gz")
    extract_dir = os.path.join(DOWNLOAD_DIR, f"{filename}-extracted/")

    if os.path.exists(extract_dir):
        log.info(f"{filename} already extracted. Skipping.")
        return os.path.join(extract_dir, f"{appname}-gnome-theme")

    if not os.path.exists(zipfile):
        log.error(f"Release zip doesn't exist: {zipfile}")
        raise FileNotFoundError

    with tarfile.open(zipfile) as tar:
        tar.extractall(path=extract_dir, filter="data")

    # Must rename the inner folder to "firefox-gnome-theme" for the provided script to work. Otherwise the theme won't show properly
    with os.scandir(path=extract_dir) as scan:
        for each in scan:
            if each.name.startswith("rafaelmardojai-firefox-gnome-theme"):
                old = os.path.join(extract_dir, each.name)
                new = os.path.join(extract_dir, f"{appname}-gnome-theme")
                os.rename(old, new)
    log.info(f"{filename} tarball extracted successfully.")
    return new
