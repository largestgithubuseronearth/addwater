# download.py
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

import logging
from enum import Enum
from typing import Optional

from gi.repository import Gio

from addwater import info
from addwater.utils.versioning import version_str_to_tuple, version_tuple_to_str

log = logging.getLogger(__name__)


class MockOnlineManager:
    """PUBLIC METHODS"""

    def __init__(self, update_return_code: int):
        log.warning("Mock online manager created!!!")
        self.online_status = OnlineStatus(update_return_code)
        schema_id = info.APP_ID + ".Firefox"
        self.settings = Gio.Settings(schema_id=schema_id)

        self.update_version = version_str_to_tuple(self.settings.get_string("installed-version"))

    def get_updates_online(
        self,
        *args,
        **kwargs
    ) -> Enum:
        log.debug(f"returning fake status code of {self.online_status}")
        return self.online_status

    def get_release(self, base_name: str, final_name: str, tarball_url: str):
        pass

    def get_update_version(self):
        return self.update_version


class OnlineStatus(Enum):
    NO_UPDATE = 0
    UPDATED = 1
    DISCONNECTED = 2
    RATELIMITED = 3


class NetworkException(Exception):
    pass


class OnlineManagerError(Exception):
    pass


class ExtractionException(Exception):
    pass
