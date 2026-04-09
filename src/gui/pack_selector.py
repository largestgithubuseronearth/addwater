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
from addwater.apps.firefox.firefox_paths import FirefoxPack

log = logging.getLogger(__name__)


@Gtk.Template(resource_path=info.PREFIX + "/gtk/pack-selector.ui")
class PackSelector(Adw.ComboRow):
    __gtype_name__ = "WaterPackSelector"

    backend = None
    settings: Gio.Settings = None
    current_pack: FirefoxPack
    # Named to prevent recursion loop when getting prop
    inner_valid_path: bool

    def __init__(self):
        super().__init__()

        self.bind_property(
            "valid-path", self, "has-tooltip", GObject.BindingFlags.INVERT_BOOLEAN
        )

    # TODO untangle this from page with props. ideally it shouldn't need
    #      help from Page at all and all of this can be in constructor
    # TODO pass pack in directly so I don't have to check it
    def setup_list(self, firefox_path, backend):
        self.backend = backend
        self.settings = backend.get_app_settings()

        self.get_model().splice(1, 0, [p.pack_name for p in FirefoxPack])

        if not self.settings.get_boolean("autofind-paths"):
            # FIXME temp adapter path -> pack
            pack = FirefoxPack.new_from_path(firefox_path)
            if pack:
                # Offset 1 since Auto Discover is first
                i = list(FirefoxPack).index(pack) + 1
                self.set_selected(i)

    # TODO rework and simplify
    def set_package(self, row):
        selected_index = row.get_selected()
        AUTO = 0

        if selected_index == AUTO:
            self.settings.set_boolean("autofind-paths", True)
            log.info("Autofind paths enabled")
            self.valid_path = True
            self.emit("package-changed")
            return

        self.settings.set_boolean("autofind-paths", False)
        log.warning("Autofind paths disabled")

        selected = row.get_selected_item().get_string()
        for pack in FirefoxPack:
            if selected == pack.pack_name:
                path = pack.path
                log.info(f"User specified path: {path}")

                try:
                    self.backend.set_data_path(path)
                except InterfaceMisuseError as err:  # invalid path provided
                    log.error(err)
                    self.valid_path = False
                else:
                    self.valid_path = True
                    self.firefox_path = path
                    self.emit("package-changed")
                    break

    @GObject.Property(type=bool, default=False)
    def valid_path(self) -> bool:
        return self.inner_valid_path

    @valid_path.setter
    def set_valid_path(self, value: bool):
        if value:
            self.remove_css_class("error")
        else:
            # TODO what happens if we set it to false multiple times in a row?
            self.add_css_class("error")

        self.inner_valid_path = value

    @GObject.Signal(name="package-changed")
    def package_changed(self):
        pass
