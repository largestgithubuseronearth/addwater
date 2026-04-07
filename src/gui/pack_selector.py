# page.py
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
from typing import Callable, Optional

from gi.repository import Adw, Gio, GObject, Gtk

from addwater import info
from addwater.backend import InterfaceMisuseError

log = logging.getLogger(__name__)


@Gtk.Template(resource_path=info.PREFIX + "/gtk/pack-selector.ui")
class PackSelector(Adw.ComboRow):
    __gtype_name__ = "WaterPackSelector"

    FIREFOX_FORMATS: dict = None
    settings: Gio.Settings = None
    firefox_path: str = None

    # Named to prevent recursion loop when getting prop
    inner_valid_path: bool

    def __init__(self):
        super().__init__()

        self.bind_property(
            "valid-path", self, "has-tooltip", GObject.BindingFlags.INVERT_BOOLEAN
        )

    # TODO untangle this from page with props
    def setup_list(self, formats_dict, settings, firefox_path):
        self.FIREFOX_FORMATS = formats_dict
        self.settings = settings
        self.firefox_path = firefox_path

        # TODO splice into model instead
        for each in self.FIREFOX_FORMATS:
            self.get_model().append(each["name"])

        if self.settings.get_boolean("autofind-paths") is False:
            user_path = self.firefox_path

            for each in self.FIREFOX_FORMATS:
                if each["path"] == user_path:
                    i = self.FIREFOX_FORMATS.index(each) + 1
                    self.set_selected(i)

    @GObject.Property(type=bool, default=False)
    def valid_path(self) -> bool:
        return self.inner_valid_path

    @valid_path.setter
    def set_valid_path(self, value: bool):
        if value:
            self.remove_css_class("error")
        else:
            # TODO what happens if we set it to true multiple times in a row?
            self.add_css_class("error")

        self.inner_valid_path = value

    @GObject.Signal(name="package-changed")
    def package_changed(self):
        pass
