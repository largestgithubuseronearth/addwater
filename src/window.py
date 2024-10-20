# window.py
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

from os.path import exists

from addwater.page import AddWaterPage
from gi.repository import Adw, Gio, Gtk

from addwater import info

log = logging.getLogger(__name__)


@Gtk.Template(resource_path=info.PREFIX + "/gtk/window.ui")
class AddWaterWindow(Adw.ApplicationWindow):
    __gtype_name__ = "AddWaterWindow"

    main_menu = Gtk.Template.Child()
    # Use when only one page is available
    # TODO make it dynamically use a ViewStack when there are multiple pages/app plugins to display
    main_toolbar_view = Gtk.Template.Child()

    def __init__(self, backends: list, **kwargs):
        super().__init__(**kwargs)
        if info.PROFILE == "developer":
            self.add_css_class("devel")

        self.set_size_request(360, 294)  # Minimum size of window Width x Height

        self.settings = Gio.Settings(schema_id=info.APP_ID)
        if info.PROFILE == "user":
            self.settings.bind(
                "window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT
            )
            self.settings.bind(
                "window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT
            )
            self.settings.bind(
                "window-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT
            )

        for each in backends:
            data_path = each.get_data_path()
            if exists(data_path):
                self.create_firefox_page(each)
            else:
                log.critical("Data path has failed. App can't continue. Displaying error status page")
                self.error_page()

    # TODO refactor to support as many pages as possible. only supports a single page rn
    def create_firefox_page(self, firefox_backend):
        self.main_toolbar_view.set_content(None)

        firefox_page = AddWaterPage(backend=firefox_backend)

        self.main_toolbar_view.set_content(firefox_page)

    """These are only called if no profile data is found"""

    def error_page(self):
        page = self.create_error_page()
        self.main_toolbar_view.set_content(page)

    def create_error_page(self):
        help_page_button = Adw.Clamp(
            hexpand=False,
            child=Gtk.Button(
                label="Open Help Page",
                action_name="app.open-help-page",
                css_classes=["suggested-action", "pill"],
            ),
        )
        statuspage = Adw.StatusPage(
            title="Firefox Profile Data Not Found",
            description="Please ensure Firefox is installed and Add Water has permission to access your profiles.",
            child=help_page_button,
        )
        return statuspage
