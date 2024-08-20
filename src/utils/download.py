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

from os.path import join, exists
from .paths import DOWNLOAD_DIR
from typing import Optional

# FIXME why is log not working at all?
log = logging.getLogger('download.py')

def get_release(base_name: str, final_path: str, tarball_url: str):
    zipfile = join(DOWNLOAD_DIR, f'{base_name}.tar.gz')
    extract_path = join(DOWNLOAD_DIR, f'{base_name}-extracted')

    log.info(f'Getting release: {app_name} v{version}.')

    if not exists(extract_path):
        try:
            _download_release(tarball_url, zipfile)
        except requests.RequestException as err:
            log.error(err)
            raise exc.NetworkException('Download failed.')

        try:
            _extract_release(zipfile, extract_path)
        except (FileNotFoundError, tarfile.TarError) as err:
            log.critical(err)
            # TODO find a better error to throw
            raise RuntimeError('Theme files failed to extract')

    # rename inner folder
    _rename_theme_folder(extract_path, final_name)

    log.info('Successfully got the release. Returning to backend...')


"""PRIVATE FUNCTIONS"""

# TODO how to make download asynchronous?
def _download_release(dl_url: str, result: str) -> None:
    """Download file and write to a file

    Args:
        dl_url = url to the file to download
        result = path to write the contents of the downloaded file
    """
    print('download')
    if exists(result):
        log.debug('Already downloaded this release. Skipping download.')
        return

    # TODO use stream feature
    response = requests.get(dl_url)

    with open(file=result, mode="wb") as file:
        file.write(response.content)

    print('download2')
    log.debug("Successfully downloaded release from Github")


def _extract_release(zipfile_path: str, result_path: str) -> None:
    """Extracts tar.gz files. It's important to know that this destroys the tar after the extraction is done.

    Args:
        zipfile_path = input tar.gz file to unzip
        result_path = resulting extracted directory
    """

    if not exists(zipfile_path):
        raise FileNotFoundError('Zipfile does not exist')
    if exists(result_path):
        log.debug('unzipped directory already exists. Skipping extraction.')
        return

    with tarfile.open(zipfile_path) as tf:
        tf.extractall(path=result_path, filter="data")
    log.debug(f'Successfully unzipped the file to {result_path}')

    os.remove(zipfile_path)
    log.debug(f'Deleted {zipfile_path}')


def _rename_theme_folder(parent_dir: str, new_name: str) -> None:
    """Renames the inner folder of the release to be easy to find later."""
    if not exists(parent_dir):
        raise FileNotFoundError('Rename failed. Parent folder does not exist.')
    if exists(new_name):
        log.debug('Inner file is already properly named. Skipping rename step.')
        return

    with os.scandir(path=parent_dir) as scan:
        for each in scan:
            if each.name.startswith(f"rafaelmardojai-{appname}-gnome-theme"):
                old = join(parent_dir, each.name)
                os.rename(old, new_name)
    log.debug('Successfully renamed inner folder')
