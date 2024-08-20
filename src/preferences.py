# preferences.py
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

import gi
import logging

gi.require_version('Xdp', '1.0')
gi.require_version('XdpGtk4', '1.0')

from gi.repository import Adw, Gtk, Gio, GLib, Xdp, XdpGtk4
from .utils.paths import FIREFOX_PATHS


log = logging.getLogger(__name__)

@Gtk.Template(resource_path="/dev/qwery/AddWater/gtk/preferences.ui")
class AddWaterPreferences(Adw.PreferencesDialog):
    __gtype_name__ = "AddWaterPreferences"

    FIREFOX_VERSIONS = FIREFOX_PATHS

    firefox_package_combobox = Gtk.Template.Child()
    firefox_package_combobox_list = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        log.info("Preferences Window activated")

        self.settings = Gio.Settings(schema_id="dev.qwery.AddWater")
        self.settings_firefox = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox")

        self.firefox_path = self.settings.get_string("firefox-path")
        self._init_firefox_combobox()

        # TODO notify of selected_item changing and deal with it in the handler
        self.firefox_package_combobox.notify("selected-item")
        self.firefox_package_combobox.connect("notify::selected-item", self._set_firefox_package)


    def _init_firefox_combobox(self):
        for each in self.FIREFOX_VERSIONS:
            self.firefox_package_combobox_list.append(each["name"])

        if self.settings.get_boolean("autofind-paths") is False:
            user_path = self.firefox_path

            for each in self.FIREFOX_VERSIONS:
                if each["path"] == user_path:
                    i = self.FIREFOX_VERSIONS.index(each) + 1

            self.firefox_package_combobox.set_selected(i)


    def _set_firefox_package(self, row, _):
        selected_index = row.get_selected()
        # First option is always Automatically Discover
        if selected_index == 0:
            self.settings.set_boolean("autofind-paths", True)
            log.warning("Autofind paths enabled")
            print("Autofind paths enabled")
            return

        self.settings.set_boolean("autofind-paths", False)
        log.warning("Autofind paths disabled")
        print("Autofind paths disabled")
        selected = row.get_selected_item().get_string()

        for each in self.FIREFOX_VERSIONS:
            if selected == each["name"]:
                print(f'User specified path: {each["path"]}')
                self.settings.set_string("firefox-path", each["path"])
                self.firefox_path = each["path"]

