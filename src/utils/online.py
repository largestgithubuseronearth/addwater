# online.py
# TODO Ensure requests follow github api specifications for params and headers. Don't upset Github!

# This is for functions that connect to the internet


from datetime import datetime, timezone
from gi.repository import GLib, Gio
from . import paths
import logging
import json
import os.path
import requests

# FIXME why does this logger not go to the file?
log = logging.getLogger(__name__)

theme_urls = {
            "firefox": "https://api.github.com/repos/rafaelmardojai/firefox-gnome-theme/releases",
            "thunderbird": "https://api.github.com/repos/rafaelmardojai/thunderbird-gnome-theme/releases"
}

DL_CACHE = paths.DOWNLOAD_DIR

def check_for_updates(app):
    """Check theme github for new releases

    Args:
    app = String, the proper name of the app. e.g. "firefox", "thunderbird"

    Returns:
        None = No new release to update to
        Int = Next release version to update to
    """
    try:
        app = app.lower()
        check_url = theme_urls[app]
    except KeyError as err:
        log.error(f"Checking for updates FAILED: Invalid app [{app}]")
        return


    # TODO are these request error types correctly syntaxed?
    try:
        latest_release = requests.get((check_url)).json()[0]
    except json.JSONDecodeError as err:
        log.error("JSON decoding of response failed")
        return False
    except requests.RequestException as err:
        log.error("Connection failed", err)
        return False

    update_version = int(latest_release["tag_name"].lstrip("v"))

    installed_version = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox").get_int("installed-version")
    if update_version > installed_version:
        log.info(f"Update available ({installed_version} → {update_version}). Downloading now...")
        download_release(
            tarball_url=latest_release["tarball_url"],
            app=app,
            version=update_version
        )
    else:
        log.info("No update available.")

    return update_version




# TODO how to make download asynchronous? Is that even worthwhile?
def download_release(tarball_url, app, version):
    response = requests.get(tarball_url) # ASYNC use stream flag
    if response.status_code != 200:
        log.error(f"Github download request gave bad response [{response.status_code}]")
        return False

    p = os.path.join(DL_CACHE, f"{app}-{version}.tar.gz")
    with open(file=p, mode="wb") as file:
        file.write(response.content)

    log.info("Github download SUCCESS!")
    return True

