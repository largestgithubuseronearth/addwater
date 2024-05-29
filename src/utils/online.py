# online.py

# This is for functions that connect to the internet

theme_urls = {
            "firefox": "https://api.github.com/repos/rafaelmardojai/firefox-gnome-theme/releases",
            "thunderbird": "https://api.github.com/repos/rafaelmardojai/thunderbird-gnome-theme/releases"
}

from datetime import datetime, timezone
from gi.repository import GLib
import json
# FIXME No module named 'requests'. How to import PIP modules?
import requests

def check_for_updates(app):
    # TODO return time and version of new fgt release
    # TODO Compare against current fgt version
    try:
        check_url = theme_urls[app]
    except KeyError as err:
        print(f"Checking for updates FAILED: Invalid app [{app}]")

    # TODO improve this request to follow github api specification
    latest_release = requests.get((check_url)).json()[0]
    new_version = int(latest_release["tag_name"].lstrip("v"))
    new_time = datetime.fromisoformat(latest_release["published_at"])


    # current = TODO make file in user data directory
    #TODO Ensure this goes to the valid flatpak directory NOT user local directory. Will likely work when run in Builder.
    # with open(file=(GLib.get_user_data_dir() + "/current_release.json"), mode="+") as file:

    # TODO TEMP REMOVE
    current = json.load(open(file="/var/home/qwery/Downloads/temp/current_release.json"))

    current_version = int(current["tag_name"].lstrip("v"))
    current_time = datetime.fromisoformat(current["published_at"])

    print(new_version, new_time, "\n\n\n", current_version, current_time)



def download_latest():
    pass


# DEBUG
def main():
    check_for_updates(app="firefox")
    download_latest()



main()
