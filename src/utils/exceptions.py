# exceptions.py
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

class AddWaterException(Exception):
    # TODO log info

    # TODO User-friendly error message

    def __init__(self, user_msg=None, log_info=None):
        self.msg = user_msg
        self.log_info = log_info
        print(self.log_info)


class InstallException(AddWaterException):
    pass

class APIException(AddWaterException):
    pass

class FatalPageException(AddWaterException):
    pass

class FatalBackendException(AddWaterException):
    pass

