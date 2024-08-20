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

# TODO refactor this whole class and how it creates the page

import logging
import os.path
import shutil
from gi.repository import Adw, Gtk, GLib, Gio, Gdk, GObject
from .addwater_page import AddWaterPage
from .backend import AddWaterBackend
from .theme_options import FIREFOX_OPTIONS
from .utils import logs, paths, installers
from .utils import exceptions as exc

log = logging.getLogger(__name__)

firefox_url = "https://api.github.com/repos/rafaelmardojai/firefox-gnome-theme/releases"


@Gtk.Template(resource_path='/dev/qwery/AddWater/gtk/window.ui')
class AddWaterWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AddWaterWindow'

    firefox_page = None     # Keep a reference to the page to call it in case of reset app.
    firefox_backend = None

    # Use when only one page is available
    main_toolbar_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Gio.Settings(schema_id="dev.qwery.AddWater")

        reset_action = Gio.SimpleAction.new("reset-app")
        reset_action.connect("activate", self.on_reset_action)
        self.add_action(reset_action)

        self.create_firefox_page()


    def create_firefox_page(self):
        self.main_toolbar_view.set_content(None)

        # Find Firefox Profile Path
        firefox_path = os.path.expanduser(self.settings.get_string("firefox-path"))
        if os.path.exists(firefox_path) is False:
            log.warning(f"Prior Firefox path no longer exists {firefox_path}")
            if self.settings.get_boolean("autofind-paths") is True:
                log.warning("Automatically finding a new one...")
                firefox_path = self.find_app_path(paths.FIREFOX_PATHS)
            else:
                log.warning("User has autofind disabled.")
                firefox_path = None
        log.info(f"Found Firefox Path: {firefox_path}")

        # Add page to window
        try:
            self.settings.set_string("firefox-path", firefox_path)
            self.firefox_backend = AddWaterBackend(
                app_path=firefox_path,
                app_name='Firefox',
                app_options=FIREFOX_OPTIONS,
                theme_url=firefox_url,
                installer=installers.firefox_installer
            )

            self.firefox_page = AddWaterPage(
                app_name='Firefox',
                backend=self.firefox_backend
            )
        except exc.FatalPageException as err:
            log.critical("Could not find Firefox path. Displaying error page to user.")
            self.firefox_page = self.error_status_page("Firefox")

        self.main_toolbar_view.set_content(self.firefox_page)


    def find_app_path(self, path_list):
        """Iterates over all common Firefox config directories and returns which one exists.

        Args:
            path_list = Either of the list of dicts from the paths module to make it easy to iterate over
        """
        for each in path_list:
            p = each["path"]
            if os.path.exists(p):
                n = each["name"]
                log.info(f"Found new Firefox path: {n} — {p}")
                return p
        log.error("Could not find any of the common Firefox paths")
        return None


    def on_reset_action(self, action, _):
        # TODO refactor this to actually close the app completely. It's awkward to ask the user to relaunch the app.

        # Delete Download cache. Always keep the logs!
        log.warning("App is being reset...")
        try:
            shutil.rmtree(paths.DOWNLOAD_DIR)
        except FileNotFoundError:
            pass
        log.info(f"Deleted path: {paths.DOWNLOAD_DIR}")

        # # Reset GSettings
        firefox_settings = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox")
        firefox_settings.reset("installed-version")
        firefox_settings.reset("theme-enabled")
        firefox_settings.reset("color-theme")
        for group in FIREFOX_OPTIONS:
            for each in group["options"]:
                firefox_settings.reset(each["key"])
        log.info("Reset all Firefox GSettings")

        self.settings.reset("firefox-path")
        self.settings.reset("autofind-paths")
        log.info("Reset AddWater GSettings")

        self.firefox_backend._reset_full_uninstall()

        self.main_toolbar_view.set_content(
            Adw.StatusPage(title="Please close and reopen Add Water")
        )

        log.info("Reset done")


    def error_status_page(self, app_name):
        statuspage = Adw.StatusPage(
            title=f"Can't Find {app_name} Data",
            description=f'Please ensure that [Preferences > {app_name}: Package Type] is correctly set to the type of {app_name} you have (Snap, Flatpak, etc.) or to Auto.\n\nFor more troubleshooting support, click the button below.',
            child=Adw.Clamp(
                maximum_size=300,
                child=Gtk.Button(
                    label="Open Help Page",
                    action_name="app.open-help-page",
                    css_classes=["suggested-action", "pill"],
                )
            )
        )
        return statuspage

