# online.py
#
# Copyright 2025 Qwery
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later


import json
import logging
import os
import shutil
import tarfile
from enum import Enum
from os.path import exists, join
from typing import Optional

import requests
from addwater.utils.paths import DOWNLOAD_DIR
from addwater.utils.versioning import version_str_to_tuple, version_tuple_to_str

from addwater import info

log = logging.getLogger(__name__)


# TODO make this handle requests asynchronously and use callbacks to report the status
# This would allow the app to launch instantly, even if internet speed is poor


class OnlineManager:
    """Handles everything to do with polling for theme updates and downloading
    release packages. It will also handle prepping those releases for the installer to use.
    """

    update_version: tuple
    theme_url: str

    def __init__(self, theme_url: str):
        log.debug("online manager is now alive")
        self.theme_url = theme_url

    """PUBLIC METHODS"""

    def get_updates_online(self, installed_version: tuple, path_info: tuple) -> Enum:
        log.info("Checking for updates...")
        self.update_version = installed_version

        try:
            update_info = self._get_release_info(self.theme_url)
        except NetworkException:
            return OnlineStatus.DISCONNECTED

        # Decide whether we need to update or not
        calls_left = update_info["ratelimit_remaining"]
        if self._is_ratelimit_exceeded(calls_left):
            log.warning("rate limiting self to avoid angering Github")
            return OnlineStatus.RATELIMITED

        files_downloaded = exists(join(path_info[0], path_info[1], path_info[2]))

        if (
            self._is_update_available(update_info["version"], installed_version)
            or not files_downloaded
        ):
            log.info("update available. getting it now...")
            self.update_version = update_info["version"]
            return self._begin_download(path_info, update_info["tarball_url"])

        log.info("no update available")
        return OnlineStatus.NO_UPDATE

    def get_update_version(self):
        return self.update_version

    """PRIVATE METHODS"""

    def _begin_download(self, path_info, tarball_url) -> Enum:
        # Update if necessary
        # TODO simplify to just pass the path info into get_release
        base_path = join(path_info[0], path_info[1])
        final_name = path_info[2]
        try:
            self._get_release(
                base_path=base_path, final_name=final_name, tarball_url=tarball_url
            )
            return OnlineStatus.UPDATED
        except NetworkException as err:
            return OnlineStatus.DISCONNECTED
        except ExtractionException as err:
            log.error(err)
            return OnlineStatus.OTHER_ERROR  # TODO handle this error better

    def _get_release(self, base_path: str, final_name: str, tarball_url: str) -> None:
        """Download and prep a theme release for installation
        Args:
                base_name = the naming convention for the download zipfile and extracted path
                final_path = naming convention for the resulting theme files. As of now,
                        this is '{app_name}-gnome-theme'. This means you can find the theme
                        folder at "{base-name}-extracted/{final_path}"
        """
        zipfile = f"{base_path}.tar.gz"
        extract_path = f"{base_path}"
        final_path = join(extract_path, final_name.lower())

        log.info(f"Getting release...")

        if not exists(zipfile) or not exists(extract_path):
            try:
                self._download_tarball(tarball_url, zipfile)
            except (requests.RequestException, requests.ConnectionError) as err:
                log.error(err)
                raise NetworkException(err)

        try:
            shutil.rmtree(final_path)
        except FileNotFoundError:
            pass

        try:
            self._extract_tarball(zipfile, extract_path)
        except (FileNotFoundError, tarfile.TarError) as err:
            raise ExtractionException("Theme files failed to extract")

        # rename inner folder
        self._rename_theme_folder(extract_path, final_name)

        log.info("Update files downloaded and ready to install.")

    @staticmethod
    def _download_tarball(dl_url: str, result: str) -> None:
        """Download file and write to a file

        Args:
                dl_url = url to the file to download
                result = path to write the contents of the downloaded file
        """
        if exists(result):
            log.debug("Already downloaded this release. Skipping download.")
            return

        headers = {
            "X-Github-Api-Version": "2022-11-28",
            "User-Agent": (info.APP_ID + "/" + info.VERSION),
            "Accept": "application/vnd.github.x-gzip+json",  # Note: I'm not sure if this is an acceptable way to do it'
        }
        response = requests.get(dl_url, headers=headers, timeout=10)

        with open(file=result, mode="wb") as file:
            file.write(response.content)

        log.debug("Successfully downloaded release from Github")

    @staticmethod
    def _extract_tarball(zipfile_path: str, result_path: str) -> None:
        """Extracts tar.gz files. It's important to know that this destroys the tar after the extraction is done.

        Args:
                zipfile_path = input tar.gz file to unzip
                result_path = resulting extracted directory
        """

        if not exists(zipfile_path):
            raise FileNotFoundError(
                "Zipfile does not exist to be extracted. It must have been lost since downloading it"
            )

        with tarfile.open(zipfile_path) as tf:
            tf.extractall(path=result_path, filter="data")
        log.debug(f"Successfully unzipped the file to {result_path}")

        os.remove(zipfile_path)
        log.debug(f"Deleted {zipfile_path}")

    @staticmethod
    def _rename_theme_folder(parent_dir: str, new_name: str) -> None:
        """Renames the inner folder of the release to be easy to find later."""
        final_path = join(parent_dir, new_name)
        if not exists(parent_dir):
            raise FileNotFoundError("Rename failed. Parent folder does not exist.")
        if exists(final_path):
            log.debug("Inner file is already properly named. Skipping rename step.")
            return

        with os.scandir(path=parent_dir) as scan:
            for each in scan:
                if each.name.startswith("rafaelmardojai"):
                    old_path = join(parent_dir, each.name)
                    os.rename(old_path, final_path)
        log.debug("Successfully renamed inner folder")

    @staticmethod
    def _get_release_info(gh_url: str) -> dict:
        """Poll Github url and check if a new release of the theme is available

        Args:
                gh_url = fully-qualified url to a github api releases endpoint

        Returns:
                release_info = dict including "version" as int, "ratelimit_remaining" as int, and "tarball_url" as str
        """
        # TODO If you can check Firefox version easily, check that before polling GH

        headers = {
            "X-Github-Api-Version": "2022-11-28",
            "User-Agent": (info.APP_ID + "/" + info.VERSION),
            "Accept": "application/vnd.github+json",
        }
        try:
            response = requests.get(gh_url, headers=headers, timeout=10)
        except requests.RequestException as err:
            # TODO use specific exceptions to handle being disconnected. It'll
            # 	be more helpful if the issue isn't just being offline but an API or
            # 	programmer error
            log.error(f"Could not connect to Github to grab release info: {err}")
            raise NetworkException(err)

        api_calls_left = int(response.headers["x-ratelimit-remaining"])
        try:
            latest_release = response.json()[0]
            version = version_str_to_tuple(latest_release["tag_name"])
            tarball_url = latest_release["tarball_url"]
        except requests.JSONDecodeError as err:
            log.error(err)
            version = None
            tarball_url = None

        # TODO make this a tuple instead for easy unpacking
        release_info = {
            "version": version,
            "ratelimit_remaining": api_calls_left,
            "tarball_url": tarball_url,
        }
        return release_info

    @staticmethod
    def _is_ratelimit_exceeded(api_calls_left: int) -> bool:
        # TODO Set API limit more robust and strict before flathub release
        # Maybe set the time and api calls remaining in gsettings. There is
        # only a warning and no mechanism stopping user from continuing to spam.
        CHOSEN_LIMIT = 10
        log.debug(f"Remaining Github API calls for the next hour: {api_calls_left}")
        return bool(api_calls_left < CHOSEN_LIMIT)

    @staticmethod
    def _is_update_available(new: tuple, current: tuple) -> bool:
        if not isinstance(current, tuple) or not isinstance(new, tuple):
            raise ValueError

        for n, c in zip(new, current):
            if n > c:
                return True

        return False


class OnlineStatus(Enum):
    NO_UPDATE = 0
    UPDATED = 1
    DISCONNECTED = 2
    RATELIMITED = 3
    OTHER_ERROR = 4


class NetworkException(Exception):
    pass


class OnlineManagerError(Exception):
    pass


class ExtractionException(Exception):
    pass
