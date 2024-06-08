# online.py
# TODO Ensure requests follow github api specifications for params and headers. Don't upset Github!
# TODO Should I skip saving the json file and just write the current theme version into gsettings?

# This is for functions that connect to the internet


from datetime import datetime, timezone
from gi.repository import GLib
from . import paths
import json
import requests


theme_urls = {
            "firefox": "https://api.github.com/repos/rafaelmardojai/firefox-gnome-theme/releases",
            "thunderbird": "https://api.github.com/repos/rafaelmardojai/thunderbird-gnome-theme/releases"
}

DL_CACHE = paths.CACHE_DOWNLOADS

def check_for_updates(app):
    try:
        check_url = theme_urls[app]
    except KeyError as err:
        print(f"Checking for updates FAILED: Invalid app [{app}]")
        return


    # TODO are these error types correctly syntaxed?
    try:
        latest_release = requests.get((check_url)).json()[0]
    except JSONDecodeError as err:
        print("JSON decoding of response failed")
    except RequestException as err:
        print("Connection failed", err)

    new_version = int(latest_release["tag_name"].lstrip("v"))
    new_time = datetime.fromisoformat(latest_release["published_at"])

    try:
        with open(file=(DL_CACHE + f"/{app}_latest.json"), mode="r", encoding="utf-8") as file:
            file = json.load(file)
            current_version = int(file["tag_name"].lstrip("v"))
            current_time = datetime.fromisoformat(file["published_at"])
    # TODO How to raise explicit error if file doesn't exist?
    except:
        print("No json details to compare new release to current. Writing new file for this latest release.")
        download_release(release_json=latest_release,
                        app=app,
                        version=new_version
                        )
        return

    if (new_version > current_version and new_time > current_time):
        print("Update available")
        download_release(release_json=latest_release,
                        app=app,
                        version=new_version)
        return True
    else:
        print("No update available")
        return False


# TODO how to make download asynchronous? Is that even worthwhile?
def download_release(release_json, app, version):

    with open(file=(DL_CACHE + f"{app}_latest.json"), mode="w", encoding="utf-8") as file:
        file.write(json.dumps(release_json))

    response = requests.get(release_json["tarball_url"])
    if response.status_code == 200:
        print("Github download is good!")
        with open(file=(DL_CACHE + f"{app}-{version}.tar.gz"), mode="wb") as file:
            file.write(response.content)
    else:
        print(f"Github download request gave bad response [{response.status_code}]")

