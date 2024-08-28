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


from enum import Enum
from typing import Optional

class MockOnlineManager():

    """PUBLIC METHODS"""

    def __init__(self, fails: bool):
        self.fails = fails


    def get_updates_online(self, installed_version: int, app_name: str) -> Enum:
        if self.fails:
            return OnlineStatus.DISCONNECTED
        elif not self.fails:
            return OnlineStatus.NO_UPDATE

    # TODO improve to allow files to be downloaded that aren't necessarily zipped or are of different ziptypes
    def get_release(self, base_name: str, final_name: str, tarball_url: str):
        pass


    def get_update_version(self,):
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
