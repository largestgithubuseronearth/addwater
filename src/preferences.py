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

import logging

import gi

gi.require_version("Xdp", "1.0")

from gi.repository import Adw, Gio, Gtk, Xdp, GObject

from addwater import info
from addwater.backend import InterfaceMisuseError

log = logging.getLogger(__name__)


@Gtk.Template(resource_path=info.PREFIX + "/gtk/preferences.ui")
class AddWaterPreferences(Adw.PreferencesDialog):
    __gtype_name__ = "AddWaterPreferences"

    background_update_switch = Gtk.Template.Child()
    firefox_package_combobox = Gtk.Template.Child()
    firefox_package_combobox_list = Gtk.Template.Child()

    def __init__(self, firefox_backend):
        # TODO improve to use all backends
        super().__init__()
        log.info("Preferences Window activated")
        self.settings_app = Gio.Settings(schema_id=info.APP_ID)
        self.settings_firefox = firefox_backend.get_app_settings()
        self.FIREFOX_FORMATS = firefox_backend.get_package_formats()
        self.firefox_backend = firefox_backend

        self.portal = Xdp.Portal()

        try:
            self.settings_app.bind(
                "background-update",
                self.background_update_switch,
                "active",
                Gio.SettingsBindFlags.DEFAULT,
            )
            self.background_update_switch.connect(
                "activated", self._do_background_request
            )
        except Exception as err:
            log.error(err)

        self.firefox_path = self.firefox_backend.get_data_path()
        self._init_firefox_combobox()

        self.firefox_package_combobox.notify("selected-item")
        self.firefox_package_combobox.connect(
            "notify::selected-item", self._set_firefox_package
        )

    # TODO is there a better way to handle this? copied from adwsteamgtk
    def _do_background_request(self, _):
        """Request permission from portals to launch at login time"""
        bg_enabled = self.settings_app.get_boolean("background-update")
        if bg_enabled:
            flag = Xdp.BackgroundFlags.AUTOSTART
        else:
            flag = Xdp.BackgroundFlags.NONE

        self.portal.request_background(
            None,
            "Checking for theme updates",
            ["addwater", "--quick-update"],
            flag,
            None,
            None,
            None,
        )

    def _init_firefox_combobox(self):
        for each in self.FIREFOX_FORMATS:
            self.firefox_package_combobox_list.append(each["name"])

        if self.settings_firefox.get_boolean("autofind-paths") is False:
            user_path = self.firefox_path

            for each in self.FIREFOX_FORMATS:
                if each["path"] == user_path:
                    i = self.FIREFOX_FORMATS.index(each) + 1
                    self.firefox_package_combobox.set_selected(i)

    def _set_firefox_package(self, row, _):
        # TODO clean this up to accomodate new signal

        selected_index = row.get_selected()
        AUTO = 0

        if selected_index == AUTO:
            self.settings_firefox.set_boolean("autofind-paths", True)
            log.info("Autofind paths enabled")
            row.remove_css_class("error")
            row.set_has_tooltip(False)
            self.emit("refresh-gui")
            return

        self.settings_firefox.set_boolean("autofind-paths", False)
        log.warning("Autofind paths disabled")

        # TODO try using index instead of strcmp. Must ensure the order cannot
        # be different though.
        selected = row.get_selected_item().get_string()
        for each in self.FIREFOX_FORMATS:
            if selected == each["name"]:
                path = each["path"]
                log.info(f'User specified path: {each["path"]}')

                try:
                    self.firefox_backend.set_data_path(path)
                except InterfaceMisuseError as err:  # invalid path provided
                    log.error(err)
                    row.add_css_class("error")
                    row.set_has_tooltip(True)
                else:
                    row.remove_css_class("error")
                    row.set_has_tooltip(False)

                self.firefox_path = path
                self.emit("refresh-gui")
                break

    @GObject.Signal(name="refresh-gui")
    def refresh_gui(self):
        pass
