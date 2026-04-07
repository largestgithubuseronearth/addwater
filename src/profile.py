# profile.py
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

from gi.repository import GObject
from gi.repository.GObject import ParamFlags
from pathlib import Path


class Profile(GObject.Object):
    __gtype_name__ = "WaterProfile"

    name = GObject.Property(
        type=str, flags=(ParamFlags.CONSTRUCT_ONLY | ParamFlags.READWRITE)
    )

    # This is called "Path" by Firefox.
    id = GObject.Property(
        type=str, flags=(ParamFlags.CONSTRUCT_ONLY | ParamFlags.READWRITE)
    )
    # TODO make this a GObject prop?
    path: Path

    favorite = GObject.Property(
        type=bool,
        default=False,
        flags=(ParamFlags.CONSTRUCT_ONLY | ParamFlags.READWRITE)
    )

    # TODO make this an enum or something
    package = GObject.Property(
        type=str, flags=(ParamFlags.CONSTRUCT_ONLY | ParamFlags.READWRITE)
    )

    # TODO convert pathstrs to Path here
    def __init__(self, name, id, path, favorite, package):
        super().__init__(name=name, id=id, favorite=favorite, package=package)
        self.path = Path(path)
