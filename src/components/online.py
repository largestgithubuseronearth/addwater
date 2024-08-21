# download.py
#
# Copyright 2024 Qwery
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

# TODO Maybe it would make sense to make this an object that can monitor the download
# itself. This may make it easier to manage async downloading.

import os
import tarfile
import logging
import requests

from enum import Enum
from os.path import join, exists
from ..utils.paths import DOWNLOAD_DIR
from typing import Optional

log = logging.getLogger(__name__)

class OnlineManager():

    installed_version: int
    update_version: int
    theme_url: str
    online_status: Enum # TODO should this class keep track of its own network status? Would that help?

    def __init__(self, theme_url: str):
        log.debug('online manager is now alive')
        self.theme_url = theme_url
        pass


    """PUBLIC METHODS"""
    def get_update_version(self,):
        return self.update_version


    def get_updates_online(self, installed_version: int, app_name: str) -> Enum:
        log.info('Checking for updates...')
        try:
            update_info = self._get_release_info(self.theme_url)
        except NetworkException as err:
            log.error(err)
            return OnlineStatus.DISCONNECTED

        update_version = update_info["version"]
        self.update_version = update_version
        ratelimit_remaining = update_info["ratelimit_remaining"]
        tarball_url=update_info["tarball_url"]

        if self._is_ratelimit_exceeded(ratelimit_remaining):
            log.warning('Rate limiting self to avoid angering Github')
            return OnlineStatus.RATELIMITED

        if self._is_update_available(new=update_version, current=installed_version):
            log.info('Update available. Getting it now...')
            base_name = f'{app_name}-{update_version}'
            final_name = f'{app_name}-gnome-theme'
            self.get_release(
                base_name=base_name,
                final_name=final_name,
                tarball_url=tarball_url
            )
            return OnlineStatus.UPDATED

        log.info('No update available.')
        return OnlineStatus.NO_UPDATE


    def get_release(self, base_name: str, final_name: str, tarball_url: str):
        """Download and prep a theme release for installation
        Args:
            base_name = the naming convention for the download zipfile and extracted path
            final_path = naming convention for the resulting theme files. As of now,
                this is '{app_name}-gnome-theme'. This means you can find the theme
                folder at "{base-name}-extracted/{final_path}"
        """
        zipfile = join(DOWNLOAD_DIR, f'{base_name}.tar.gz')
        extract_path = join(DOWNLOAD_DIR, f'{base_name}-extracted')

        log.info(f'Getting release: {base_name}')

        if not exists(extract_path):
            try:
                self._download_release(tarball_url, zipfile)
            except requests.RequestException as err:
                raise NetworkException(err)

            try:
                self._extract_release(zipfile, extract_path)
            except (FileNotFoundError, tarfile.TarError) as err:
                # TODO find a better error to throw
                raise ('Theme files failed to extract')

        # rename inner folder
        self._rename_theme_folder(extract_path, final_name)


    """PRIVATE FUNCTIONS"""
    # TODO how to make download asynchronous?
    @staticmethod
    def _download_release(dl_url: str, result: str) -> None:
        """Download file and write to a file

        Args:
            dl_url = url to the file to download
            result = path to write the contents of the downloaded file
        """
        if exists(result):
            log.debug('Already downloaded this release. Skipping download.')
            return

        # TODO use stream feature
        response = requests.get(dl_url)

        with open(file=result, mode="wb") as file:
            file.write(response.content)

        log.debug("Successfully downloaded release from Github")


    @staticmethod
    def _extract_release(zipfile_path: str, result_path: str) -> None:
        """Extracts tar.gz files. It's important to know that this destroys the tar after the extraction is done.

        Args:
            zipfile_path = input tar.gz file to unzip
            result_path = resulting extracted directory
        """

        if not exists(zipfile_path):
            raise FileNotFoundError('Zipfile does not exist to be extracted. It must have been lost since downloading it')
        if exists(result_path):
            log.debug('Unzipped directory already exists. Skipping extraction.')
            return

        with tarfile.open(zipfile_path) as tf:
            tf.extractall(path=result_path, filter="data")
        log.debug(f'Successfully unzipped the file to {result_path}')

        os.remove(zipfile_path)
        log.debug(f'Deleted {zipfile_path}')


    @staticmethod
    def _rename_theme_folder(parent_dir: str, new_name: str) -> None:
        """Renames the inner folder of the release to be easy to find later."""
        final_path = join(parent_dir, new_name)
        if not exists(parent_dir):
            raise FileNotFoundError('Rename failed. Parent folder does not exist.')
        if exists(final_path):
            log.debug('Inner file is already properly named. Skipping rename step.')
            return

        with os.scandir(path=parent_dir) as scan:
            for each in scan:
                if each.name.startswith(f"rafaelmardojai-{new_name}"):
                    old_path = join(parent_dir, each.name)
                    os.rename(old_path, final_path)
        log.debug('Successfully renamed inner folder')


    @staticmethod
    def _get_release_info(gh_url: str) -> dict[str, [int,str]]:
        """Poll Github url and check if a new release of the theme is available

        Args:
            gh_url = full url to a github releases api call (api.github.com/...)

        Returns:
            release_info = dict including "version" as int, "ratelimit_remaining" as int, and "tarball_url" as str
        """
        # TODO If you can check Firefox version easily, check that before requesting from GH

        # TODO make sure this request is complaint with github's specification
        # Include all the applicable headers
        response = requests.get((gh_url))

        latest_release = response.json()[0]
        api_calls_left = int(response.headers["x-ratelimit-remaining"])
        version = int(latest_release["tag_name"].lstrip("v"))
        tarball_url = latest_release["tarball_url"]

        release_info = {
            "version" : version,
            "ratelimit_remaining" : api_calls_left,
            "tarball_url" : tarball_url,
        }
        return release_info


    @staticmethod
    def _is_ratelimit_exceeded(api_calls_left: int):
        # TODO Set API limit more robust and strict before flathub release
        CHOSEN_LIMIT = 10
        log.debug(f'Remaining Github API calls for the next hour: {api_calls_left}')
        return bool(api_calls_left < CHOSEN_LIMIT)


    @staticmethod
    def _is_update_available(current: int, new: int):
        # TODO consider making this consider special cases like rollbacks or partial updates
        return bool(new > current)


class OnlineStatus(Enum):
    NO_UPDATE = 0
    UPDATED = 1
    DISCONNECTED = 2
    RATELIMITED = 3


class NetworkException(Exception):
    pass

class ExtractionException(Exception):
    pass
