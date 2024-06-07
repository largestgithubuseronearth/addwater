# online.py

# This is for functions that connect to the internet

theme_urls = {
            "firefox": "https://api.github.com/repos/rafaelmardojai/firefox-gnome-theme/releases",
            "thunderbird": "https://api.github.com/repos/rafaelmardojai/thunderbird-gnome-theme/releases"
}

from datetime import datetime, timezone
from gi.repository import GLib
import json
import requests

def check_for_updates(app):
    try:
        check_url = theme_urls[app]
    except KeyError as err:
        print(f"Checking for updates FAILED: Invalid app [{app}]")
        return


    # TODO improve this request to follow github api specification for params and headers
    # TODO are these error types correctly syntaxed?
    try:
        latest_release = requests.get((check_url)).json()[0]
    except JSONDecodeError as err:
        print("JSON decoding of response failed")
    except RequestException as err:
        print("Connection failed", err)

    new_version = int(latest_release["tag_name"].lstrip("v"))
    new_time = datetime.fromisoformat(latest_release["published_at"])

    with open(file=(GLib.get_user_data_dir() + "/current_release.json")) as file:
        file = json.load(file)
        current_version = int(file["tag_name"].lstrip("v"))
        current_time = datetime.fromisoformat(file["published_at"])


    if new_version > current_version and new_time > current_time:
        print("Update available")
        return True
    else:
        print("No update available")
        return False


def download_latest():
    # TODO how to make this asynchronous? Is that even worthwhile?
    # TODO When downloading, save the new release json file to data dir
    pass
